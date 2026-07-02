import io

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


class ImageService:
    DEFAULT_FORMAT = "JPEG"
    DEFAULT_COLOR = "blue"

    @classmethod
    def create_image(cls, width=2000, height=2000, filename="test.jpg"):
        buffer = io.BytesIO()

        image = Image.new("RGB", (width, height), cls.DEFAULT_COLOR)

        image.save(buffer, cls.DEFAULT_FORMAT)

        buffer.seek(0)

        return SimpleUploadedFile(
            filename,
            buffer.read(),
            content_type="image/jpeg"
        )
