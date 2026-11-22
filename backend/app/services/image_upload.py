from pathlib import Path

MAX_IMAGE_SIZE = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

IMAGE_SIGNATURES = {
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".webp": (b"RIFF",)
}


def validate_image(filename: str, content: bytes):
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Định dạng ảnh không được hỗ trợ")

    if not content:
        raise ValueError("Ảnh tải lên bị trống")

    if len(content) > MAX_IMAGE_SIZE:
        raise ValueError("Dung lượng ảnh vượt quá 5MB")

    signatures = IMAGE_SIGNATURES[extension]

    if not any(content.startswith(sig) for sig in signatures):
        raise ValueError("Nội dung file không đúng định dạng ảnh")

    if extension == ".webp" and content[8:12] != b"WEBP":
        raise ValueError("File WebP không hợp lệ")

    return True