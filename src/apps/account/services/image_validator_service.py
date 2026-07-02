from PIL import Image


class ImageValidator:

    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    @classmethod
    def validate_size(cls, file):
        if file.size > cls.MAX_FILE_SIZE:
            raise ValueError("Image file too large. Maximum allowed size is 5MB.")

    @classmethod
    def validate_extension(cls, filename):

        ext = filename.split(".")[-1].lower()

        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError("Invalid image extension.")

    @staticmethod
    def validate_image(file):

        try:
            img = Image.open(file)
            img.verify()
        except Exception:
            raise ValueError("Invalid image file.")