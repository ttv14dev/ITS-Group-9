"""Kiểu dữ liệu vào, ra của API nhận diện."""
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class VehicleType(str, Enum):
    ambulance = "ambulance"
    firetruck = "firetruck"
    police = "police"


class Detection(BaseModel):
    """Một phương tiện tìm thấy trong ảnh."""

    index: int  # số thứ tự, trùng với số vẽ trên ảnh
    vehicle_type: VehicleType  # loại sau cùng (đã xét dấu hiệu xe ưu tiên)
    label_vi: str
    is_priority: bool
    score: float  # xe ưu tiên: điểm dấu hiệu; xe thường: độ tin cậy của mô hình
    box: list[int]  # [x, y, rộng, cao] theo pixel của ảnh gốc
    note: Optional[str] = None  # lý do nhận ra dấu hiệu ưu tiên


class FrameResult(BaseModel):
    """Kết quả của một khung hình được lấy mẫu từ video."""

    time_s: float
    vehicles: int
    is_priority: bool
    vehicle_type: Optional[VehicleType] = None
    score: float = 0.0


class VideoInfo(BaseModel):
    duration_s: float
    frames_analyzed: int
    priority_frames: int
    max_vehicles: int
    timeline: list[FrameResult]


class DetectionResult(BaseModel):
    is_priority: bool
    # None khi không phát hiện được phương tiện nào
    vehicle_type: Optional[VehicleType] = None
    label_vi: str
    # Với nhận diện theo danh sách, người dùng tự chọn nên không có độ tin cậy (None)
    confidence: Optional[float] = None
    # danh_sach: người dùng chọn | phan_tich_anh | phan_tich_video
    mode: str
    message: str = ""
    detections: list[Detection] = []
    video: Optional[VideoInfo] = None
    # Ảnh đã vẽ khung quanh phương tiện (data URL JPEG), dùng cho ảnh và khung hình tiêu biểu của video
    annotated_image: Optional[str] = None

