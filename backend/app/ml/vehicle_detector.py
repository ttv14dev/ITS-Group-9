import os
from ultralytics import YOLO


class VehicleDetector:
    def __init__(self, model_path="yolov8n.pt", confidence_threshold=0.5):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None

        self.vehicle_classes = {
            "car": "car",
            "motorcycle": "motorcycle",
            "bus": "bus",
            "truck": "truck"
        }

    def load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        self.model = YOLO(self.model_path)
        return True

    def detect(self, image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        if self.model is None:
            self.load_model()

        results = self.model.predict(
            source=image_path,
            conf=self.confidence_threshold,
            verbose=False
        )

        detections = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = self.model.names[class_id]

                if class_name in self.vehicle_classes:
                    detections.append({
                        "vehicle_type": self.vehicle_classes[class_name],
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