"""Các API nhận diện."""
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from backend.app.core import config
from backend.app.ml.yolo_detector import ModelUnavailable
from backend.app.schemas.detection import DetectionResult
from backend.app.services import detector

router = APIRouter(prefix="/api", tags=["detection"])

# Chữ ký đầu file để biết đúng là ảnh/video (không tin đuôi file hay Content-Type)
IMAGE_SIGNATURES = {
    "JPEG": lambda d: d[:3] == b"\xff\xd8\xff",
    "PNG": lambda d: d[:8] == b"\x89PNG\r\n\x1a\n",
    "WEBP": lambda d: d[:4] == b"RIFF" and d[8:12] == b"WEBP",
}


def _image_format(data: bytes):
    return next((name for name, check in IMAGE_SIGNATURES.items() if check(data)), None)


def _looks_like_video(data: bytes) -> bool:
    head = data[:16]
    return (
        head[4:8] == b"ftyp"  # mp4, mov
        or head[:4] == b"\x1a\x45\xdf\xa3"  # mkv, webm
        or (head[:4] == b"RIFF" and head[8:11] == b"AVI")  # avi
    )


@router.get("/health")
def health():
    return {"status": "ok", "detector": "yolov8n (3 lop: cuu thuong, cuu hoa, cong an)"}


@router.post("/detect/image", response_model=DetectionResult)
async def detect_by_image(file: UploadFile = File(...)):
    # Đọc tối đa MAX + 1 byte để biết file có vượt giới hạn hay không
    data = await file.read(config.MAX_UPLOAD_BYTES + 1)
    if len(data) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"Ảnh quá lớn, tối đa {config.MAX_UPLOAD_MB} MB.")
    if not data:
        raise HTTPException(400, "File rỗng.")
    if _image_format(data) is None:
        raise HTTPException(415, "Chỉ nhận ảnh JPG, PNG hoặc WEBP hợp lệ.")
    try:
        return await run_in_threadpool(detector.detect_by_image, data)
    except ModelUnavailable as exc:
        raise HTTPException(503, str(exc))
    except ValueError as exc:
        raise HTTPException(415, str(exc))


@router.post("/detect/video", response_model=DetectionResult)
async def detect_by_video(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in config.ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(415, "Chỉ nhận video MP4, AVI, MOV, MKV hoặc WEBM.")
    data = await file.read(config.MAX_VIDEO_BYTES + 1)
    if len(data) > config.MAX_VIDEO_BYTES:
        raise HTTPException(413, f"Video quá lớn, tối đa {config.MAX_VIDEO_MB} MB.")
    if not data:
        raise HTTPException(400, "File rỗng.")
    if not _looks_like_video(data):
        raise HTTPException(415, "File không phải video hợp lệ.")

    # OpenCV cần đọc video từ đường dẫn: lưu tạm, xử lý xong là xóa (không lưu lịch sử)
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = config.UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    temp_path.write_bytes(data)
    try:
        return await run_in_threadpool(detector.detect_by_video, str(temp_path))
    except ModelUnavailable as exc:
        raise HTTPException(503, str(exc))
    except ValueError as exc:
        raise HTTPException(415, str(exc))
    finally:
        temp_path.unlink(missing_ok=True)

