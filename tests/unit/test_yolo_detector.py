"""Kiểm thử phần xử lý ảnh vào, kết quả ra của mô hình YOLOv8 (không cần ảnh thật)."""
import numpy as np

from backend.app.ml import yolo_detector as yd


def test_letterbox_keeps_ratio_and_pads():
    img = np.full((100, 200, 3), 255, np.uint8)  # ảnh ngang 200x100
    canvas, scale, left, top = yd.letterbox(img, 640)
    assert canvas.shape == (640, 640, 3)
    assert scale == 3.2 and left == 0 and top == 160
    assert canvas[0, 0, 0] == 114 and canvas[320, 320, 0] == 255  # viền xám, giữa là ảnh


def fake_output(rows):
    """Tạo đầu ra giả (1, 4+3, 8400); mỗi dòng là (cx, cy, w, h, điểm lớp 0, 1, 2)."""
    out = np.zeros((1, 7, 8400), np.float32)
    for i, r in enumerate(rows):
        out[0, :, i] = r
    return out


def test_decode_maps_box_back_to_original_image():
    # Khung giữa ảnh vuông 640 -> giữ nguyên toạ độ, lớp 1 = firetruck
    out = fake_output([(320, 320, 100, 80, 0.0, 0.9, 0.1)])
    boxes = yd.decode(out, scale=1.0, left=0, top=0, img_w=640, img_h=640, conf=0.5, nms=0.5)
    assert len(boxes) == 1
    b = boxes[0]
    assert b.cls == "firetruck" and abs(b.score - 0.9) < 1e-6
    assert (b.x, b.y, b.w, b.h) == (270, 280, 100, 80)


def test_decode_removes_letterbox_offset_and_scale():
    # Ảnh gốc 200x100 phóng 3.2 lần, lề trên 160: khung ở giữa -> x=100-?, y=50-?
    out = fake_output([(320, 320, 320, 160, 0.8, 0.0, 0.0)])
    boxes = yd.decode(out, scale=3.2, left=0, top=160, img_w=200, img_h=100, conf=0.5, nms=0.5)
    b = boxes[0]
    assert b.cls == "ambulance"
    assert (b.x, b.y, b.w, b.h) == (50, 25, 100, 50)


def test_decode_filters_low_confidence_and_overlaps():
    out = fake_output([
        (200, 200, 100, 100, 0.0, 0.0, 0.9),   # police, giữ lại
        (203, 202, 100, 100, 0.0, 0.0, 0.6),   # gần như trùng khung trên -> bị NMS loại
        (500, 500, 100, 100, 0.2, 0.1, 0.1),   # điểm thấp -> bị lọc
    ])
    boxes = yd.decode(out, 1.0, 0, 0, 640, 640, conf=0.5, nms=0.5)
    assert [b.cls for b in boxes] == ["police"]


def test_decode_clips_box_to_image():
    out = fake_output([(10, 10, 100, 100, 0.9, 0.0, 0.0)])
    b = yd.decode(out, 1.0, 0, 0, 640, 640, conf=0.5, nms=0.5)[0]
    assert b.x == 0 and b.y == 0 and b.w == 60 and b.h == 60


def test_real_model_loads_and_returns_list():
    # Mô hình ONNX thật: ảnh trơn thì không có xe ưu tiên
    img = np.full((240, 320, 3), (90, 140, 90), np.uint8)
    assert yd.YoloDetector().detect(img) == []
