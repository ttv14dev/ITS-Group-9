import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.image_upload import validate_image
from app.ml.vehicle_detector import VehicleDetector


router = APIRouter()

detector = VehicleDetector()

# Đường dẫn đến ITS-Group-9-New/storage/uploads
UPLOAD_DIR = Path(__file__).resolve().parents[4] / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/image")
async def detect_image(file: UploadFile = File(...)):
    temp_path = None

    try:
        # Đọc nội dung ảnh
        content = await file.read()

        # Kiểm tra định dạng, kích thước và nội dung ảnh
        extension = validate_image(file.filename, content)

        # Tạo file tạm trong storage/uploads
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=extension,
            prefix="upload_",
            dir=UPLOAD_DIR,
            delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        # Nhận diện phương tiện
        result = detector.detect(temp_path)

        return result

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Image detection failed: {str(error)}"
        )

    finally:
        await file.close()

        # Xóa ảnh tạm sau khi xử lý
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)