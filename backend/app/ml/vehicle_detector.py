from pathlib import Path
from ultralytics import YOLO


class VehicleDetector:
    def __init__(self, model_path="yolov8n.pt", confidence_threshold=0.25):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None

        self.vehicle_classes = {
            "car",
            "motorcycle",
            "bus",
            "truck"
        }

    def load_model(self):
        """Tải model YOLO."""
        if self.model is None:
            self.model = YOLO(self.model_path)

    def detect(self, image_path: str):
        """Nhận diện phương tiện trong ảnh."""
        path = Path(image_path)

        if not path.is_file():
            raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")

        self.load_model()

        results = self.model.predict(
            source=str(path),
            conf=self.confidence_threshold,
            verbose=False
        )

        detections = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                vehicle_type = result.names[class_id]

                if vehicle_type in self.vehicle_classes:
                    detections.append({
                        "vehicle_type": vehicle_type,
                        "confidence": confidence
                    })

        if not detections:
            return {
                "is_priority": False,
                "vehicle_type": "unknown",
                "confidence": 0.0
            }

        best_detection = max(
            detections,
            key=lambda item: item["confidence"]
        )

        return {
            "is_priority": False,
            "vehicle_type": best_detection["vehicle_type"],
            "confidence": round(best_detection["confidence"], 4)
        }