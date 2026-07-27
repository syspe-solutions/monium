from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image


class ImageProcessor:
    MAX_SIZE = (512, 512)
    MAX_IMAGE_PIXELS = 10_000_000  # 10 Megapixels

    def __init__(self):
        Image.MAX_IMAGE_PIXELS = self.MAX_IMAGE_PIXELS

    def resize(self, image_file):
        image = Image.open(image_file)
        
        # Manter o modo de cor correto (RGB para JPEG)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
        image.thumbnail(self.MAX_SIZE, Image.LANCZOS)
        buffer = BytesIO()
        
        # Mantém o formato original ou usa JPEG como padrão
        img_format = image.format if image.format else "JPEG"
        image.save(buffer, format=img_format, quality=90)

        # Garantir o Content-Type correto baseado no formato real da imagem
        actual_format = img_format.lower()
        if actual_format == "jpg":
            actual_format = "jpeg"
        content_type = f"image/{actual_format}"
        
        content_file = ContentFile(buffer.getvalue())
        content_file.content_type = content_type # Isso ajuda o S3 a identificar o arquivo corretamente

        return content_file

    def resize_square(self, image_file, size=512):
        """Recorta para 1:1 (centralizado no menor lado) e reduz para um quadrado
        de até `size`px — usado por logos/ícones que precisam ser sempre quadrados."""
        image = Image.open(image_file)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        width, height = image.size
        side = min(width, height)
        left = (width - side) // 2
        top = (height - side) // 2
        image = image.crop((left, top, left + side, top + side))
        image.thumbnail((size, size), Image.LANCZOS)

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=90)

        content_file = ContentFile(buffer.getvalue())
        content_file.content_type = "image/jpeg"

        return content_file
