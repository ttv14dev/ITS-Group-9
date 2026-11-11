"""Cấu hình chung của ứng dụng (đọc từ biến môi trường, có giá trị mặc định)."""
import os
from pathlib import Path

# Thư mục gốc của dự án (ITS-Group-9)
BASE_DIR = Path(__file__).resolve().parents[3]

FRONTEND_DIR = BASE_DIR / "frontend"
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"

# mock = mô phỏng, clip = mô hình CLIP thật
DETECTOR = os.getenv("DETECTOR", "mock").lower()

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

# Định dạng ảnh được phép (tên định dạng do Pillow trả về -> đuôi file)
ALLOWED_IMAGE_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
