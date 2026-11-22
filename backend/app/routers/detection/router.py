"""Các API nhận diện."""
import io
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from backend.app.core import config
from backend.app.schemas.detection import (
    DetectByTypeRequest,
    DetectionResult,
    VehicleTypeInfo,
)
from backend.app.services import detector

router = APIRouter(prefix="/api", tags=["detection"])


@router.get("/health")
def health():
    return {"status": "ok", "detector": config.DETECTOR}


@router.get("/vehicle-types", response_model=list[VehicleTypeInfo])
def vehicle_types():
    return detector.list_vehicle_types()


@router.post("/detect/type", response_model=DetectionResult)
def detect_by_type(body: DetectByTypeRequest):
    return detector.detect_by_type(body.vehicle_type)


@router.post("/detect/image", response_model=DetectionResult)
async def detect_by_image(file: UploadFile = File(...)):
    # Đọc tối đa MAX + 1 byte để biết file có vượt giới hạn hay không
    data = await file.read(config.MAX_UPLOAD_BYTES + 1)
    if len(data) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"Ảnh quá lớn, tối đa {config.MAX_UPLOAD_MB} MB.")
    if not data:
        raise HTTPException(400, "File rỗng.")

    # Kiểm tra đúng là ảnh (không tin đuôi file hay Content-Type do người dùng gửi)
    try:
        with Image.open(io.BytesIO(data)) as img:
            img.verify()
            fmt = img.format
    except (UnidentifiedImageError, OSError):
        raise HTTPException(415, "File không phải ảnh hợp lệ.")
    if fmt not in config.ALLOWED_IMAGE_FORMATS:
        raise HTTPException(415, "Chỉ nhận ảnh JPG, PNG hoặc WEBP.")

    # Lưu tạm vào storage/uploads để xử lý, xong là xóa (hệ thống không lưu lịch sử)
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = config.UPLOAD_DIR / f"{uuid.uuid4().hex}{config.ALLOWED_IMAGE_FORMATS[fmt]}"
    temp_path.write_bytes(data)
    try:
        return detector.detect_by_image(temp_path.read_bytes(), file.filename or "")
    finally:
        temp_path.unlink(missing_ok=True)
