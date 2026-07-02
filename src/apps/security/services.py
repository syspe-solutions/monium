import secrets
import time
import uuid
from datetime import timedelta
from urllib.parse import urlparse

import redis

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import check_password, make_password

from apps.account.models import User
from apps.security.models import PasswordResetOTP, PasswordResetTimeToken

BASE_DELAY = 15


class RedisConnectionService:
    @staticmethod
    def get_redis_client():
        return redis.Redis.from_url(settings.REDIS_URL)


class ExponentialBanService:
    @staticmethod
    def register_lockout(username):
        key = f"ban:{username}:count"

        client = RedisConnectionService.get_redis_client()
        count = client.incr(key)

        delay = BASE_DELAY * (2 ** (count - 1))

        ban_key = f"ban:{username}:until"
        client.setex(ban_key, delay, int(time.time()) + delay)

        return delay

    @staticmethod
    def get_ban_remaining(username):
        client = RedisConnectionService.get_redis_client()
        ban_key = f"ban:{username}:until"
        ts = client.get(ban_key)
        if not ts:
            return 0
        now = int(time.time())
        return max(0, int(ts) - now)


class WebSocketOriginService:

    @staticmethod
    def _normalized_allowed_origins() -> set[str]:
        return {
            origin.lower().rstrip("/")
            for origin in getattr(settings, "ALLOWED_WS_ORIGINS", [])
        }

    @staticmethod
    def extract_base_origin(origin: str) -> str | None:
        try:
            parsed = urlparse(origin)
            if not parsed.scheme or not parsed.netloc:
                return None
            return f"{parsed.scheme}://{parsed.netloc}".lower()
        except Exception:
            return None

    @staticmethod
    def is_allowed(origin: str | None) -> bool:
        if not origin:
            return False

        base_origin = WebSocketOriginService.extract_base_origin(origin)
        if not base_origin:
            return False

        return base_origin in WebSocketOriginService._normalized_allowed_origins()



class PasswordResetSessionService:
    SESSION_USER_KEY = "password_reset_user_id"
    SESSION_VERIFIED_KEY = "password_reset_verified"

    @staticmethod
    def set_user(request, user):
        request.session[PasswordResetSessionService.SESSION_USER_KEY] = str(user.id)
        request.session[PasswordResetSessionService.SESSION_VERIFIED_KEY] = False
        request.session.modified = True

    @staticmethod
    def get_user(request):
        user_id = request.session.get(PasswordResetSessionService.SESSION_USER_KEY)
        if not user_id:
            return None
        return User.objects.filter(id=user_id, is_active=True).first()

    @staticmethod
    def mark_verified(request):
        request.session[PasswordResetSessionService.SESSION_VERIFIED_KEY] = True
        request.session.modified = True

    @staticmethod
    def is_verified(request) -> bool:
        return request.session.get(
            PasswordResetSessionService.SESSION_VERIFIED_KEY, False
        )

    @staticmethod
    def clear(request):
        request.session.pop(PasswordResetSessionService.SESSION_USER_KEY, None)
        request.session.pop(PasswordResetSessionService.SESSION_VERIFIED_KEY, None)
        request.session.modified = True

class PasswordResetTimeTokenService:
    EXPIRATION_MINUTES = 10

    @staticmethod
    def generate(otp: PasswordResetOTP) -> str:
        
        PasswordResetTimeToken.objects.filter(otp=otp).delete()
        
        token = uuid.uuid4().hex

        PasswordResetTimeToken.objects.create(
            otp=otp,
            token=token,
            expires_at=timezone.now() + timedelta(
                minutes=PasswordResetTimeTokenService.EXPIRATION_MINUTES
            ),
        )

        return token

_DUMMY_OTP_HASH = make_password("__dummy__")

class PasswordResetOTPService:

    MAX_ATTEMPTS = 5
    EXPIRATION_MINUTES = 10

    @staticmethod
    def generate(user) -> str:
        code = f"{secrets.randbelow(1_000_000):06d}"

        new_otp = PasswordResetOTP.objects.create(
            user=user,
            code_hash=make_password(code),
            expires_at=timezone.now() + timedelta(minutes=PasswordResetOTPService.EXPIRATION_MINUTES),
            attempts=0,
            used=False,
        )

        PasswordResetOTP.objects.filter(
            user=user,
            used=False,
        ).exclude(pk=new_otp.pk).update(used=True)

        return code

    @staticmethod
    def validate(user, raw_code) -> PasswordResetOTP:
        try:
            otp = PasswordResetOTP.objects.filter(
                user=user,
                used=False,
            ).latest("created_at")
        except PasswordResetOTP.DoesNotExist:
            check_password(raw_code, _DUMMY_OTP_HASH)  # tempo constante
            raise ValueError("Código inválido ou expirado.")

        if otp.expires_at < timezone.now():
            otp.used = True
            otp.save(update_fields=["used"])
            raise ValueError("Código expirado.")

        if otp.attempts >= PasswordResetOTPService.MAX_ATTEMPTS:
            otp.used = True
            otp.save(update_fields=["used"])
            raise ValueError("Número máximo de tentativas excedido.")

        if not check_password(raw_code, otp.code_hash):
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            raise ValueError("Código inválido.")

        otp.used = True
        otp.save(update_fields=["used"])

        return otp