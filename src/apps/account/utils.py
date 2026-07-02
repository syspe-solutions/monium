import os
import random
from abc import ABC
from datetime import datetime

from django.contrib.auth import authenticate, get_user_model
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class AbstractLoginData(ABC):
    identifier: str
    password: str


class ProfileUtils:
    @staticmethod
    def generate_image_path(instance, filename):
        _, filename_ext = os.path.splitext(filename)
        return f"profile_images/{slugify(instance.user.username)}_{datetime.now().date()}{filename_ext}"

    @staticmethod
    def get_random_profile_image(self):
        image_dir = 'media/profile_images'
        if not os.path.exists(image_dir):
            return 'default.png'
        image_files = os.listdir(image_dir)
        if image_files:
            return os.path.join('profile_images', random.choice(image_files))
        return 'default.png'


class AuthenticationUtils:
    @staticmethod
    def authenticate(credentials: AbstractLoginData):
        User = get_user_model()
        user = None
        user = authenticate(username=credentials.identifier,
                            password=credentials.password)
        if user is None:
            try:
                user_obj = User.objects.get(email=credentials.identifier)
                user = authenticate(
                    username=user_obj.username, password=credentials.password)
            except User.DoesNotExist:
                pass

        return user

    @staticmethod
    def validate_password(password: str):
        if len(password) < 8:
            raise ValueError(_("The password must be at least 8 characters long."))

        if not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            raise ValueError(_("The password must contain both letters and numbers."))

        if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in password):
            raise ValueError(
                _("The password must contain at least one special character."))