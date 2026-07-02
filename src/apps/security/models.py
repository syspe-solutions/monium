from django.conf import settings
from django.db import models

from apps.common.models import BaseModelAbstract


class PasswordResetOTP(BaseModelAbstract):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    used = models.BooleanField(default=False)


class PasswordResetTimeToken(BaseModelAbstract):
    otp = models.OneToOneField(
        PasswordResetOTP,
        related_name='reset_token',
        on_delete=models.CASCADE
    )
    token = models.CharField(
        max_length=255,
        null=True
    )
    expires_at = models.DateTimeField()