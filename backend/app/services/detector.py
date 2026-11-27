"""Dịch vụ nhận diện phương tiện ưu tiên.

Quy trình cho mỗi ảnh:
  1. Tiếp nhận ảnh.
  2. Chuẩn hóa ảnh về 640x640 (giữ tỉ lệ, chèn viền).
  3. Mô hình YOLOv8n đã huấn luyện cho ra khung, loại xe (cứu thương / cứu hỏa / công an) và độ tin cậy.
  4. Lọc theo ngưỡng tin cậy và loại các khung trùng nhau (NMS).
  5. Xuất kết quả (kèm ảnh đã vẽ khung).
"""
import base64
import math
from collections import Counter

import cv2
import numpy as np

from backend.app.core import config
from backend.app.ml.yolo_detector import get_detector
from backend.app.schemas.detection import (
    DetectionResult,
    Detection,
    FrameResult,
    VehicleType,
    VideoInfo,
)

LABELS_VI = {
    VehicleType.ambulance: "Xe cứu thương",
    VehicleType.firetruck: "Xe cứu hỏa",
    VehicleType.police: "Xe công an",
}
PRIORITY = {VehicleType.ambulance, VehicleType.firetruck, VehicleType.police}


# ---------- Nhận diện trên một khung hình ----------
def analyze_frame(bgr: np.ndarray) -> list[Detection]:
    """Chạy mô hình YOLOv8 trên một khung hình, trả về các xe ưu tiên tìm thấy."""
    detections: list[Detection] = []
    for i, box in enumerate(get_detector().detect(bgr), start=1):
        vtype = VehicleType(box.cls)
        detections.append(
            Detection(
                index=i,
                vehicle_type=vtype,
                label_vi=LABELS_VI[vtype],
                is_priority=vtype in PRIORITY,
                score=round(box.score, 2),
                box=[box.x, box.y, box.w, box.h],
            )
        )
    return detections


def draw_annotated(bgr: np.ndarray, detections: list[Detection], max_width: int = 960) -> str:
    """Vẽ khung (đỏ: xe ưu tiên) và số thứ tự, trả về data URL JPEG."""
    img = bgr.copy()
    thick = max(2, round(max(img.shape[:2]) / 400))
    for d in detections:
        x, y, w, h = d.box
        color = (40, 40, 220) if d.is_priority else (60, 160, 40)  # BGR
        cv2.rectangle(img, (x, y), (x + w, y + h), color, thick)
        label = str(d.index)
        scale = max(0.6, thick / 2.2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, scale, thick)
        y0 = max(y - th - 8, 0)
        cv2.rectangle(img, (x, y0), (x + tw + 10, y0 + th + 8), color, -1)
        cv2.putText(img, label, (x + 5, y0 + th + 2), cv2.FONT_HERSHEY_SIMPLEX, scale,
                    (255, 255, 255), thick, cv2.LINE_AA)
    if img.shape[1] > max_width:
        ratio = max_width / img.shape[1]
        img = cv2.resize(img, (max_width, int(img.shape[0] * ratio)))
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()


def _main_detection(detections: list[Detection]) -> Detection:
    """Xe được chọn làm kết quả chính: xe ưu tiên có độ tin cậy cao nhất, nếu không có thì xe lớn nhất."""
    priority = [d for d in detections if d.is_priority]
    if priority:
        return max(priority, key=lambda d: d.score)
    return max(detections, key=lambda d: d.box[2] * d.box[3])


def _message(detections: list[Detection]) -> str:
    if not detections:
        return "Không phát hiện xe ưu tiên nào trong ảnh."
    names = ", ".join(f"{d.label_vi} (số {d.index}, {round(d.score * 100)}%)" for d in detections)
    return f"Phát hiện {len(detections)} xe ưu tiên: {names}."


# ---------- Nhận diện ảnh ----------
def decode_image(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Không đọc được ảnh.")
    return img


def detect_by_image(data: bytes) -> DetectionResult:
    bgr = decode_image(data)
    detections = analyze_frame(bgr)
    annotated = draw_annotated(bgr, detections)
    if not detections:
        return DetectionResult(
            is_priority=False, vehicle_type=None, label_vi="Không phát hiện xe ưu tiên",
            confidence=None, mode="phan_tich_anh", message=_message(detections),
            detections=[], annotated_image=annotated,
        )
    main = _main_detection(detections)
    return DetectionResult(
        is_priority=main.is_priority, vehicle_type=main.vehicle_type, label_vi=main.label_vi,
        confidence=main.score, mode="phan_tich_anh", message=_message(detections),
        detections=detections, annotated_image=annotated,
    )


# ---------- Nhận diện video ----------
def detect_by_video(path: str) -> DetectionResult:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError("Không mở được video (định dạng hoặc codec không được hỗ trợ).")
    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps != fps or fps <= 0 or fps > 240:
            fps = 25.0
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        limit_frames = int(fps * config.MAX_VIDEO_SECONDS)
        usable = min(total, limit_frames) if total > 0 else limit_frames
        # Lấy khoảng 2 khung/giây nhưng không quá MAX_VIDEO_FRAMES khung
        step = max(int(round(fps / 2)), 1)
        step = max(step, math.ceil(usable / config.MAX_VIDEO_FRAMES))

        timeline: list[FrameResult] = []
        best_score, best_frame, best_dets = -1.0, None, []
        index, last_read = 0, 0
        while index < limit_frames and len(timeline) < config.MAX_VIDEO_FRAMES:
            if not cap.grab():
                break
            last_read = index
            if index % step == 0:
                ok, frame = cap.retrieve()
                if ok:
                    dets = analyze_frame(frame)
                    pri = [d for d in dets if d.is_priority]
                    top = max(pri, key=lambda d: d.score) if pri else None
                    timeline.append(FrameResult(
                        time_s=round(index / fps, 2), vehicles=len(dets), is_priority=bool(pri),
                        vehicle_type=top.vehicle_type if top else None,
                        score=top.score if top else 0.0,
                    ))
                    # Khung tiêu biểu: khung ưu tiên điểm cao nhất, nếu không có thì khung nhiều xe nhất
                    rank = (1000 + top.score) if top else len(dets)
                    if rank > best_score:
                        best_score, best_frame, best_dets = rank, frame, dets
            index += 1
        duration = round((total / fps) if total > 0 else (last_read + 1) / fps, 2)
    finally:
        cap.release()

    if not timeline or best_frame is None:
        raise ValueError("Video không có khung hình nào đọc được.")

    pri_frames = [f for f in timeline if f.is_priority]
    needed = min(2, len(timeline))  # cần thấy ở ít nhất 2 khung hình để tránh nhận nhầm một lần
    is_priority = len(pri_frames) >= needed
    info = VideoInfo(
        duration_s=duration, frames_analyzed=len(timeline), priority_frames=len(pri_frames),
        max_vehicles=max(f.vehicles for f in timeline), timeline=timeline,
    )
    annotated = draw_annotated(best_frame, best_dets)

    if is_priority:
        weight: Counter = Counter()
        for f in pri_frames:
            weight[f.vehicle_type] += f.score
        vtype = weight.most_common(1)[0][0]
        confidence = round(sum(f.score for f in pri_frames if f.vehicle_type == vtype)
                           / max(sum(1 for f in pri_frames if f.vehicle_type == vtype), 1), 2)
        message = (f"Phát hiện {LABELS_VI[vtype].lower()} ở {len(pri_frames)}/{len(timeline)} "
                   f"khung hình đã phân tích.")
        return DetectionResult(
            is_priority=True, vehicle_type=vtype, label_vi=LABELS_VI[vtype], confidence=confidence,
            mode="phan_tich_video", message=message, detections=best_dets, video=info,
            annotated_image=annotated,
        )

    if info.max_vehicles == 0:
        return DetectionResult(
            is_priority=False, vehicle_type=None, label_vi="Không phát hiện xe ưu tiên",
            mode="phan_tich_video",
            message=f"Không thấy xe ưu tiên nào trong {len(timeline)} khung hình đã phân tích.",
            video=info, annotated_image=annotated,
        )
    # Có thấy xe ưu tiên nhưng quá ít khung hình: chưa đủ căn cứ để kết luận
    return DetectionResult(
        is_priority=False, vehicle_type=None, label_vi="Chưa đủ căn cứ kết luận",
        mode="phan_tich_video",
        message=(f"Chỉ thấy dấu hiệu xe ưu tiên ở {len(pri_frames)}/{len(timeline)} khung hình "
                 f"(cần ít nhất {needed}) nên chưa kết luận là có xe ưu tiên."),
        detections=best_dets, video=info, annotated_image=annotated,
    )
