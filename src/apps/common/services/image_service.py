from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image


class ImageService:
    def __init__(self):
        pass

    def resize_image(
        self,
        image_file,
        size: tuple[int, int],
        format="JPEG",
        quality=85
    ) -> ContentFile:

        img = Image.open(image_file)
        img = img.convert("RGB")
        img.thumbnail(size, Image.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, format=format, quality=quality)
        buffer.seek(0)

        return ContentFile(buffer.read())
