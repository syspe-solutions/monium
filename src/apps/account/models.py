import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModelAbstract


class User(BaseModelAbstract, AbstractUser):
    email = models.EmailField(_("email address"), unique=True)

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

class UserDeletionSchedule(BaseModelAbstract):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)


def user_avatar_upload_path(instance, filename):
    ext = filename.split(".")[-1].lower()
    return f"avatars/{instance.user.id}/{uuid.uuid4().hex}.{ext}"


class UserProfile(BaseModelAbstract):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    avatar = models.ImageField(
        upload_to=user_avatar_upload_path,
        null=True,
        blank=True
    )

    bio = models.TextField(
        max_length=500,
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    birth_date = models.DateField(
        null=True,
        blank=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.user.username} profile"
