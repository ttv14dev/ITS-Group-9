"""Dùng chung cho các test: bộ phát hiện giả để test chạy nhanh và ổn định."""
import numpy as np
import pytest

from backend.app.ml.yolo_detector import Box


class FakeYolo:
    """Luôn trả về một xe ưu tiên nằm giữa ảnh; cls=None nghĩa là không thấy xe nào."""

    def __init__(self, cls="ambulance", score=0.9):
        self.cls, self.score = cls, score

    def detect(self, bgr: np.ndarray):
        if self.cls is None:
            return []
        h, w = bgr.shape[:2]
        return [Box(self.cls, self.score, w // 8, h // 8, w * 3 // 4, h * 3 // 4)]


@pytest.fixture
def fake_yolo(monkeypatch):
    """Gọi fake_yolo('firetruck') để chọn loại xe giả, fake_yolo(None) để không thấy xe nào."""
    from backend.app.services import detector

    def install(cls="ambulance", score=0.9):
        monkeypatch.setattr(detector, "get_detector", lambda: FakeYolo(cls, score))

    return install
