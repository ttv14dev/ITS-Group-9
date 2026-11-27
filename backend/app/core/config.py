"""Cấu hình chung của ứng dụng (đọc từ biến môi trường, có giá trị mặc định)."""
import os
from pathlib import Path

# Thư mục gốc của dự án (ITS-Group-9)
BASE_DIR = Path(__file__).resolve().parents[3]

FRONTEND_DIR = BASE_DIR / "frontend"
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

MAX_VIDEO_MB = int(os.getenv("MAX_VIDEO_MB", "50"))
MAX_VIDEO_BYTES = MAX_VIDEO_MB * 1024 * 1024
# Chỉ phân tích tối đa chừng này giây đầu của video, và tối đa chừng này khung hình
MAX_VIDEO_SECONDS = int(os.getenv("MAX_VIDEO_SECONDS", "60"))
MAX_VIDEO_FRAMES = int(os.getenv("MAX_VIDEO_FRAMES", "40"))

# Định dạng ảnh được phép (tên định dạng do Pillow trả về -> đuôi file)
ALLOWED_IMAGE_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

# Ngưỡng tin cậy tối thiểu của mô hình để tính là phát hiện xe ưu tiên (0..1).
# Tăng lên thì ít báo nhầm hơn nhưng dễ bỏ sót hơn.
DETECT_CONF = float(os.getenv("DETECT_CONF", "0.50"))
