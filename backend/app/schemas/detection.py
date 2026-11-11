"""Kiểu dữ liệu vào, ra của API nhận diện."""
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class VehicleType(str, Enum):
    ambulance = "ambulance"
    firetruck = "firetruck"
    police = "police"
    car = "car"
    truck = "truck"
    bus = "bus"
    motorbike = "motorbike"


class DetectByTypeRequest(BaseModel):
    vehicle_type: VehicleType


class DetectionResult(BaseModel):
    is_priority: bool
    vehicle_type: VehicleType
    label_vi: str
    # Với nhận diện theo danh sách, người dùng tự chọn nên không có độ tin cậy (None)
    confidence: Optional[float] = None
    # mo_phong: kết quả mô phỏng, clip: do mô hình CLIP dự đoán, danh_sach: người dùng chọn
    mode: str


class VehicleTypeInfo(BaseModel):
    code: VehicleType
    label_vi: str
    is_priority: bool
