import pytest

from backend.app.services.image_upload import validate_image


def test_empty_image():
    with pytest.raises(ValueError):
        validate_image("test.jpg", b"")


def test_invalid_extension():
    with pytest.raises(ValueError):
        validate_image("test.txt", b"abc")


def test_invalid_image_content():
    with pytest.raises(ValueError):
        validate_image("test.jpg", b"not an image")


def test_valid_jpeg():
    content = b"\xff\xd8\xff" + b"test"
    assert validate_image("test.jpg", content) is Truepython -m pytest tests/unit/test_image_upload.py -v


def test_image_exceeds_max_size():
    content = b"\xff\xd8\xff" + b"a" * (5 * 1024 * 1024)

    with pytest.raises(ValueError, match="Dung lượng ảnh vượt quá 5MB"):
        validate_image("test.jpg", content)


