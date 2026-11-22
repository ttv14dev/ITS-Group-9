"""Kiểm thử các API (chạy bằng:  python -m pytest)."""
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.main import app

client = TestClient(app)


def make_image_bytes(fmt="PNG", size=(32, 32)):
    buf = io.BytesIO()
    Image.new("RGB", size, (200, 30, 30)).save(buf, format=fmt)
    return buf.getvalue()


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_vehicle_types_has_priority_and_normal():
    data = client.get("/api/vehicle-types").json()
    priority = {v["code"] for v in data if v["is_priority"]}
    assert priority == {"ambulance", "firetruck", "police"}
    assert any(not v["is_priority"] for v in data)


@pytest.mark.parametrize("code", ["ambulance", "firetruck", "police"])
def test_detect_type_priority(code):
    r = client.post("/api/detect/type", json={"vehicle_type": code})
    assert r.status_code == 200
    body = r.json()
    assert body["is_priority"] is True
    assert body["vehicle_type"] == code
    assert body["confidence"] is None
    assert body["mode"] == "danh_sach"


@pytest.mark.parametrize("code", ["car", "truck", "bus", "motorbike"])
def test_detect_type_normal(code):
    r = client.post("/api/detect/type", json={"vehicle_type": code})
    assert r.status_code == 200
    assert r.json()["is_priority"] is False


def test_detect_type_invalid():
    r = client.post("/api/detect/type", json={"vehicle_type": "spaceship"})
    assert r.status_code == 422


def test_detect_image_by_filename_keyword():
    files = {"file": ("xe-cuu-thuong.png", make_image_bytes("PNG"), "image/png")}
    r = client.post("/api/detect/image", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["vehicle_type"] == "ambulance"
    assert body["is_priority"] is True
    assert 0.0 <= body["confidence"] <= 1.0
    assert body["mode"] == "mo_phong"


def test_detect_image_accepts_jpeg_and_webp():
    for fmt, ext in (("JPEG", "jpg"), ("WEBP", "webp")):
        files = {"file": (f"police.{ext}", make_image_bytes(fmt), f"image/{ext}")}
        assert client.post("/api/detect/image", files=files).status_code == 200


def test_detect_image_rejects_non_image():
    files = {"file": ("note.png", b"day khong phai anh", "image/png")}
    r = client.post("/api/detect/image", files=files)
    assert r.status_code == 415


def test_detect_image_rejects_empty():
    files = {"file": ("empty.png", b"", "image/png")}
    assert client.post("/api/detect/image", files=files).status_code == 400


def test_detect_image_rejects_too_large(monkeypatch):
    from backend.app.core import config

    monkeypatch.setattr(config, "MAX_UPLOAD_BYTES", 100)
    files = {"file": ("big.png", make_image_bytes("PNG", (200, 200)), "image/png")}
    assert client.post("/api/detect/image", files=files).status_code == 413


def test_upload_is_deleted_after_detection():
    from backend.app.core import config

    before = set(config.UPLOAD_DIR.glob("*"))
    files = {"file": ("car.png", make_image_bytes("PNG"), "image/png")}
    assert client.post("/api/detect/image", files=files).status_code == 200
    assert set(config.UPLOAD_DIR.glob("*")) == before


def test_frontend_is_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "Nhận diện phương tiện ưu tiên" in r.text
