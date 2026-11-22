"""Dịch vụ nhận diện (bản mô phỏng, chưa dùng mô hình thật).

- detect_by_type: người dùng chọn loại xe -> trả kết quả ngay.
- detect_by_image: đoán loại xe từ tên file (xe-cuu-thuong.png, police.jpg...);
  nếu tên file không có từ khóa thì chọn một loại xe theo nội dung ảnh (cùng ảnh -> cùng kết quả).
"""
import hashlib
import unicodedata

from backend.app.schemas.detection import DetectionResult, VehicleType, VehicleTypeInfo

LABELS_VI = {
    VehicleType.ambulance: "Xe cứu thương",
    VehicleType.firetruck: "Xe cứu hỏa",
    VehicleType.police: "Xe công an",
    VehicleType.car: "Xe con",
    VehicleType.truck: "Xe tải",
    VehicleType.bus: "Xe buýt",
    VehicleType.motorbike: "Xe máy",
}
PRIORITY = {VehicleType.ambulance, VehicleType.firetruck, VehicleType.police}

KEYWORDS = {
    VehicleType.ambulance: ("ambulance", "cuu thuong", "cuuthuong", "cap cuu"),
    VehicleType.firetruck: ("firetruck", "fire truck", "fire-truck", "fire_truck", "cuu hoa", "cuuhoa", "chua chay"),
    VehicleType.police: ("police", "cong an", "congan", "canh sat"),
    VehicleType.bus: ("bus", "buyt", "xe buyt"),
    VehicleType.truck: ("truck", "xe tai"),
    VehicleType.motorbike: ("motorbike", "motorcycle", "xe may"),
    VehicleType.car: ("car", "xe con", "oto"),
}


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.replace("-", " ").replace("_", " ")


def list_vehicle_types() -> list[VehicleTypeInfo]:
    return [
        VehicleTypeInfo(code=t, label_vi=LABELS_VI[t], is_priority=t in PRIORITY)
        for t in VehicleType
    ]


def detect_by_type(vehicle_type: VehicleType) -> DetectionResult:
    return DetectionResult(
        is_priority=vehicle_type in PRIORITY,
        vehicle_type=vehicle_type,
        label_vi=LABELS_VI[vehicle_type],
        confidence=None,
        mode="danh_sach",
    )


def detect_by_image(data: bytes, filename: str) -> DetectionResult:
    name = _normalize(filename or "")
    found = next(
        (t for t, words in KEYWORDS.items() if any(w in name for w in words)), None
    )
    digest = hashlib.sha256(data).digest()
    if found is None:
        found = list(VehicleType)[digest[0] % len(VehicleType)]
    confidence = round(0.80 + (digest[1] % 18) / 100, 2)  # 0.80 - 0.97
    return DetectionResult(
        is_priority=found in PRIORITY,
        vehicle_type=found,
        label_vi=LABELS_VI[found],
        confidence=confidence,
        mode="mo_phong",
    )
