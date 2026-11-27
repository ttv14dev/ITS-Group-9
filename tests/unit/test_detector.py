"""Kiểm thử dịch vụ nhận diện (dùng bộ phát hiện giả)."""
import cv2
import numpy as np
import pytest

from backend.app.schemas.detection import VehicleType
from backend.app.services import detector


def encode(img, ext=".png"):
    return cv2.imencode(ext, img)[1].tobytes()


def red_img():
    img = np.zeros((240, 320, 3), np.uint8)
    img[:] = (30, 30, 200)
    return img


def test_firetruck_detected_in_image(fake_yolo):
    fake_yolo("firetruck")
    r = detector.detect_by_image(encode(red_img()))
    assert r.is_priority and r.vehicle_type == VehicleType.firetruck
    assert r.annotated_image.startswith("data:image/jpeg;base64,")
    assert r.detections[0].box[2] > 0


def test_each_priority_class_is_reported(fake_yolo):
    for cls, expected in (("ambulance", VehicleType.ambulance), ("firetruck", VehicleType.firetruck),
                          ("police", VehicleType.police)):
        fake_yolo(cls, 0.8)
        r = detector.detect_by_image(encode(red_img()))
        assert r.is_priority and r.vehicle_type == expected and r.confidence == 0.8


def test_image_without_priority_vehicle(fake_yolo):
    fake_yolo(None)
    r = detector.detect_by_image(encode(np.full((240, 320, 3), 120, np.uint8)))
    assert not r.is_priority and r.vehicle_type is None and r.detections == []


def test_undecodable_image_raises():
    with pytest.raises(ValueError):
        detector.decode_image(b"khong phai anh")


def make_video(path, frame, n=20, fps=10):
    h, w = frame.shape[:2]
    out = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    for _ in range(n):
        out.write(frame)
    out.release()


def test_video_with_firetruck(tmp_path, fake_yolo):
    fake_yolo("firetruck")
    p = tmp_path / "v.mp4"
    make_video(p, red_img())
    r = detector.detect_by_video(str(p))
    assert r.is_priority and r.vehicle_type == VehicleType.firetruck
    assert r.video.frames_analyzed >= 2 and r.video.priority_frames >= 2
    assert r.mode == "phan_tich_video"


def test_video_without_priority_vehicle(tmp_path, fake_yolo):
    fake_yolo(None)
    p = tmp_path / "v.mp4"
    make_video(p, np.full((240, 320, 3), 120, np.uint8))
    r = detector.detect_by_video(str(p))
    assert not r.is_priority and r.video.priority_frames == 0


def test_video_with_only_one_priority_frame_is_not_enough(tmp_path, monkeypatch):
    from backend.app.ml.yolo_detector import Box

    calls = {"n": 0}

    class OnceThenNothing:
        def detect(self, bgr):
            calls["n"] += 1
            return [Box("police", 0.9, 5, 5, 50, 50)] if calls["n"] == 1 else []

    monkeypatch.setattr(detector, "get_detector", lambda: OnceThenNothing())
    p = tmp_path / "v.mp4"
    make_video(p, np.full((240, 320, 3), 120, np.uint8))
    r = detector.detect_by_video(str(p))
    assert r.video.priority_frames == 1 and not r.is_priority and r.vehicle_type is None


def test_video_cannot_be_opened(tmp_path):
    p = tmp_path / "bad.mp4"
    p.write_bytes(b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 40)
    with pytest.raises(ValueError):
        detector.detect_by_video(str(p))
