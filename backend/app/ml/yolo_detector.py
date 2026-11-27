"""Nhận diện xe ưu tiên bằng YOLOv8n do nhóm tự huấn luyện (file ONNX), chạy qua OpenCV.

Mô hình có 3 lớp: Ambulance (xe cứu thương), Fire truck (xe cứu hỏa), Police car (xe công an).
Không cần PyTorch hay thư viện ultralytics khi chạy web, chỉ cần OpenCV.
Cách huấn luyện: xem docs/training/Train_YOLOv8_xe_uu_tien.ipynb.
"""
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

import cv2
import numpy as np

from backend.app.core import config

MODEL_PATH = Path(__file__).resolve().parent / "models" / "priority_yolov8n.onnx"

# Thứ tự lớp đúng với data.yaml lúc huấn luyện: 0 Ambulance, 1 Fire truck, 2 Police car
CLASSES = ["ambulance", "firetruck", "police"]


class ModelUnavailable(RuntimeError):
    """Không nạp được mô hình (thiếu file hoặc file hỏng)."""


@dataclass
class Box:
    cls: str  # ambulance / firetruck / police
    score: float  # độ tin cậy của mô hình, 0..1
    x: int
    y: int
    w: int
    h: int


def letterbox(bgr: np.ndarray, size: int = 640):
    """Thu nhỏ ảnh giữ nguyên tỉ lệ rồi chèn viền xám cho vuông (giống lúc huấn luyện).

    Trả về (ảnh vuông, tỉ lệ thu nhỏ, lề trái, lề trên).
    """
    h, w = bgr.shape[:2]
    scale = min(size / h, size / w)
    nw, nh = max(int(round(w * scale)), 1), max(int(round(h * scale)), 1)
    resized = cv2.resize(bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)
    canvas = np.full((size, size, 3), 114, dtype=np.uint8)
    left, top = (size - nw) // 2, (size - nh) // 2
    canvas[top : top + nh, left : left + nw] = resized
    return canvas, scale, left, top


def decode(output: np.ndarray, scale: float, left: int, top: int, img_w: int, img_h: int,
           conf: float, nms: float) -> list[Box]:
    """Đổi đầu ra thô (1, 4+số lớp, 8400) của YOLOv8 thành danh sách khung."""
    rows = np.squeeze(output, axis=0).T  # (8400, 4 + số lớp)
    class_scores = rows[:, 4:]
    ids = np.argmax(class_scores, axis=1)
    scores = class_scores[np.arange(len(rows)), ids]
    mask = scores >= conf
    rows, ids, scores = rows[mask], ids[mask], scores[mask]
    if len(rows) == 0:
        return []

    cx, cy, bw, bh = rows[:, 0], rows[:, 1], rows[:, 2], rows[:, 3]
    x0 = ((cx - bw / 2) - left) / scale
    y0 = ((cy - bh / 2) - top) / scale
    x1 = ((cx + bw / 2) - left) / scale
    y1 = ((cy + bh / 2) - top) / scale
    x0, x1 = np.clip(x0, 0, img_w), np.clip(x1, 0, img_w)
    y0, y1 = np.clip(y0, 0, img_h), np.clip(y1, 0, img_h)

    boxes = [[int(a), int(b), int(c - a), int(d - b)] for a, b, c, d in zip(x0, y0, x1, y1)]
    keep = cv2.dnn.NMSBoxes(boxes, scores.astype(float).tolist(), conf, nms)
    result = []
    for i in np.array(keep).flatten():
        x, y, w, h = boxes[i]
        if w < 8 or h < 8:
            continue
        result.append(Box(CLASSES[int(ids[i])], float(scores[i]), x, y, w, h))
    return sorted(result, key=lambda b: b.score, reverse=True)


class YoloDetector:
    def __init__(self, conf: float | None = None, nms: float = 0.50, size: int = 640):
        self.conf = config.DETECT_CONF if conf is None else conf
        self.nms, self.size = nms, size
        self._net = None
        self._lock = Lock()

    def _load(self):
        if self._net is not None:
            return
        if not MODEL_PATH.exists() or MODEL_PATH.stat().st_size == 0:
            raise ModelUnavailable(f"Thiếu file mô hình: {MODEL_PATH}")
        try:
            net = cv2.dnn.readNetFromONNX(str(MODEL_PATH))
        except cv2.error as exc:
            raise ModelUnavailable(f"Không đọc được file mô hình ONNX ({exc}).") from exc
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        self._net = net

    def detect(self, bgr: np.ndarray) -> list[Box]:
        """Trả về các xe ưu tiên tìm thấy trong ảnh BGR (xe thường không được nhận diện)."""
        H, W = bgr.shape[:2]
        canvas, scale, left, top = letterbox(bgr, self.size)
        blob = cv2.dnn.blobFromImage(canvas, 1 / 255.0, (self.size, self.size), swapRB=True)
        with self._lock:
            self._load()
            self._net.setInput(blob)
            output = self._net.forward()
        return decode(output, scale, left, top, W, H, self.conf, self.nms)


_detector = YoloDetector()


def get_detector() -> YoloDetector:
    return _detector
