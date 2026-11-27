"""Kiểm thử các API (chạy bằng:  python -m pytest)."""
import io

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.main import app

client = TestClient(app)


def image_bytes(fmt="PNG", color=(200, 30, 30), size=(64, 64)):
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format=fmt)
    return buf.getvalue()


def video_bytes(tmp_path, color=(30, 30, 200), n=12):
    path = tmp_path / "clip.mp4"
    out = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 10, (160, 120))
    frame = np.full((120, 160, 3), color, np.uint8)
    for _ in range(n):
        out.write(frame)
    out.release()
    return path.read_bytes()


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_detect_image_firetruck(fake_yolo):
    fake_yolo("firetruck")
    files = {"file": ("anh.png", image_bytes(), "image/png")}
    r = client.post("/api/detect/image", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["is_priority"] and body["vehicle_type"] == "firetruck"
    assert body["mode"] == "phan_tich_anh" and body["annotated_image"]


def test_result_does_not_depend_on_filename(fake_yolo):
    # Tên file ghi "xe-cuu-thuong" nhưng mô hình không thấy xe ưu tiên -> không được coi là xe ưu tiên
    fake_yolo(None)
    files = {"file": ("xe-cuu-thuong.png", image_bytes(color=(120, 120, 120)), "image/png")}
    assert client.post("/api/detect/image", files=files).json()["is_priority"] is False


def test_detect_image_accepts_jpeg_and_webp(fake_yolo):
    fake_yolo(None)
    for fmt, ext in (("JPEG", "jpg"), ("WEBP", "webp")):
        files = {"file": (f"a.{ext}", image_bytes(fmt), f"image/{ext}")}
        assert client.post("/api/detect/image", files=files).status_code == 200


def test_detect_image_real_model_on_plain_image():
    # Dùng mô hình ONNX thật: ảnh trơn không có xe ưu tiên nào
    files = {"file": ("trong.png", image_bytes(color=(90, 140, 90), size=(320, 240)), "image/png")}
    r = client.post("/api/detect/image", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["vehicle_type"] is None and body["is_priority"] is False


def test_detect_image_rejects_non_image():
    files = {"file": ("note.png", b"day khong phai anh", "image/png")}
    assert client.post("/api/detect/image", files=files).status_code == 415


def test_detect_image_rejects_empty():
    assert client.post("/api/detect/image", files={"file": ("e.png", b"", "image/png")}).status_code == 400


def test_detect_image_rejects_too_large(monkeypatch):
    from backend.app.core import config

    monkeypatch.setattr(config, "MAX_UPLOAD_BYTES", 100)
    files = {"file": ("big.png", image_bytes(size=(300, 300)), "image/png")}
    assert client.post("/api/detect/image", files=files).status_code == 413


def test_detect_video_firetruck(tmp_path, fake_yolo):
    fake_yolo("firetruck")
    files = {"file": ("clip.mp4", video_bytes(tmp_path), "video/mp4")}
    r = client.post("/api/detect/video", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["is_priority"] and body["vehicle_type"] == "firetruck"
    assert body["video"]["frames_analyzed"] >= 2 and body["mode"] == "phan_tich_video"


def test_detect_video_rejects_wrong_extension():
    files = {"file": ("clip.txt", b"abc", "text/plain")}
    assert client.post("/api/detect/video", files=files).status_code == 415


def test_detect_video_rejects_fake_video():
    files = {"file": ("clip.mp4", b"day khong phai video", "video/mp4")}
    assert client.post("/api/detect/video", files=files).status_code == 415


def test_detect_video_rejects_too_large(monkeypatch):
    from backend.app.core import config

    monkeypatch.setattr(config, "MAX_VIDEO_BYTES", 10)
    files = {"file": ("clip.mp4", b"\x00\x00\x00\x18ftypmp42" + b"0" * 100, "video/mp4")}
    assert client.post("/api/detect/video", files=files).status_code == 413


def test_uploaded_video_is_deleted_after_detection(tmp_path, fake_yolo):
    from backend.app.core import config

    fake_yolo(None)
    before = set(config.UPLOAD_DIR.glob("*")) if config.UPLOAD_DIR.exists() else set()
    files = {"file": ("clip.mp4", video_bytes(tmp_path), "video/mp4")}
    assert client.post("/api/detect/video", files=files).status_code == 200
    after = set(config.UPLOAD_DIR.glob("*")) if config.UPLOAD_DIR.exists() else set()
    assert after == before


def test_frontend_is_served():
    r = client.get("/")
    assert r.status_code == 200 and "Nhận diện phương tiện ưu tiên" in r.text

