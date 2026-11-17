import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.image_upload import validate_image
from app.ml.vehicle_detector import VehicleDetector


router = APIRouter()

detector = VehicleDetector()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@router.post("/image")
async def detect_image(file: UploadFile = File(...)):
    temp_path = None

    try:
        filename = file.filename or ""
        extension = Path(filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Định dạng ảnh không được hỗ trợ"
            )

        content = await file.read()

        try:
            validate_image(filename, content)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error))

        with tempfile.NamedTemporaryFile(
            suffix=extension,
            delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        result = detector.detect(temp_path)

        return result

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý ảnh: {str(error)}"
        )
    finally:
        await file.close()

        if temp_path and Path(temp_path).exists():
            Path(temp_path).unlink()