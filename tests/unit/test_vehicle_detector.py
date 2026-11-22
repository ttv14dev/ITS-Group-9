import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from backend.app.ml.vehicle_detector import VehicleDetector


def test_vehicle_detector_file_not_found():
    detector = VehicleDetector()

    with pytest.raises(FileNotFoundError):
        detector.detect("not_found.jpg")


def test_load_model_not_found():
    detector = VehicleDetector(model_path="not_found.pt")

    with pytest.raises(FileNotFoundError):
        detector.load_model()


@patch("backend.app.ml.vehicle_detector.YOLO")
def test_load_model_success(mock_yolo):
    detector = VehicleDetector(model_path="yolov8n.pt")

    result = detector.load_model()

    assert result is True
    mock_yolo.assert_called_once_with("yolov8n.pt")


@patch("backend.app.ml.vehicle_detector.YOLO")
def test_detect_car_success(mock_yolo, tmp_path):
    image_path = tmp_path / "car.jpg"
    image_path.write_bytes(b"fake image")

    mock_model = MagicMock()
    mock_yolo.return_value = mock_model

    mock_box = MagicMock()
    mock_box.cls = [2]
    mock_box.conf = [0.93]

    mock_result = MagicMock()
    mock_result.boxes = [mock_box]

    mock_model.predict.return_value = [mock_result]
    mock_model.names = {2: "car"}

    detector = VehicleDetector()
    detector.model = mock_model

    result = detector.detect(str(image_path))

    assert result["is_priority"] is False
    assert result["vehicle_type"] == "car"
    assert result["confidence"] == 0.93


@patch("backend.app.ml.vehicle_detector.YOLO")
def test_detect_no_vehicle(mock_yolo, tmp_path):
    image_path = tmp_path / "empty.jpg"
    image_path.write_bytes(b"fake image")

    mock_model = MagicMock()
    mock_yolo.return_value = mock_model
    mock_model.predict.return_value = [
        MagicMock(boxes=[])
    ]

    detector = VehicleDetector()
    detector.model = mock_model

    result = detector.detect(str(image_path))

    assert result == {
        "is_priority": False,
        "vehicle_type": "unknown",
        "confidence": 0.0
    }