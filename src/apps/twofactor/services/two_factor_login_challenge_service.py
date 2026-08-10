import time

from django.contrib.auth import get_user_model

User = get_user_model()


class TwoFactorLoginChallengeService:
    """Guarda, entre o passo de senha e o passo de código, qual usuário está a
    meio caminho do login — sem chamar django.contrib.auth.login() antes da
    hora. Mesmo padrão de sessão pendente já usado em
    apps.security.services.PasswordResetSessionService, mas com sua própria
    chave e um contador de tentativas (recuperação de senha não precisa disso
    porque o próprio PasswordResetOTPService já limita tentativas no OTP)."""

    SESSION_USER_KEY = "two_factor_pending_user_id"
    SESSION_NEXT_KEY = "two_factor_pending_next"
    SESSION_ATTEMPTS_KEY = "two_factor_pending_attempts"
    SESSION_BACKEND_KEY = "two_factor_pending_backend"
    SESSION_LAST_SENT_AT_KEY = "two_factor_pending_last_sent_at"

    MAX_ATTEMPTS = 5
    RESEND_COOLDOWN_SECONDS = 30

    @staticmethod
    def start(request, user, next_url: str = "") -> None:
        # `user.backend` só existe porque LoginUserService acabou de chamar
        # authenticate() com sucesso — precisa ser guardado agora e reaplicado
        # no login() final, senão o usuário perde o backend que autenticou de
        # fato (ModelBackend local vs LDAPBackend) quando recarregarmos o User
        # do banco só pelo id na etapa de verificação do código.
        request.session[TwoFactorLoginChallengeService.SESSION_USER_KEY] = str(user.pk)
        request.session[TwoFactorLoginChallengeService.SESSION_NEXT_KEY] = next_url or ""
        request.session[TwoFactorLoginChallengeService.SESSION_ATTEMPTS_KEY] = 0
        request.session[TwoFactorLoginChallengeService.SESSION_BACKEND_KEY] = getattr(
            user, "backend", "django.contrib.auth.backends.ModelBackend"
        )
        request.session.modified = True

    @staticmethod
    def get_pending_user(request):
        user_id = request.session.get(TwoFactorLoginChallengeService.SESSION_USER_KEY)
        if not user_id:
            return None
        return User.objects.filter(pk=user_id, is_active=True).first()

    @staticmethod
    def get_next_url(request) -> str:
        return request.session.get(TwoFactorLoginChallengeService.SESSION_NEXT_KEY, "")

    @staticmethod
    def get_backend(request) -> str:
        return request.session.get(
            TwoFactorLoginChallengeService.SESSION_BACKEND_KEY,
            "django.contrib.auth.backends.ModelBackend",
        )

    @staticmethod
    def code_already_sent(request) -> bool:
        return request.session.get(TwoFactorLoginChallengeService.SESSION_LAST_SENT_AT_KEY) is not None

    @staticmethod
    def mark_code_sent(request) -> None:
        request.session[TwoFactorLoginChallengeService.SESSION_LAST_SENT_AT_KEY] = time.time()
        request.session.modified = True

    @staticmethod
    def seconds_until_resend_allowed(request) -> int:
        last_sent_at = request.session.get(TwoFactorLoginChallengeService.SESSION_LAST_SENT_AT_KEY)
        if last_sent_at is None:
            return 0
        elapsed = time.time() - last_sent_at
        remaining = TwoFactorLoginChallengeService.RESEND_COOLDOWN_SECONDS - elapsed
        return max(0, int(remaining))

    @staticmethod
    def register_failed_attempt(request) -> int:
        key = TwoFactorLoginChallengeService.SESSION_ATTEMPTS_KEY
        attempts = request.session.get(key, 0) + 1
        request.session[key] = attempts
        request.session.modified = True
        return attempts

    @staticmethod
    def attempts_exhausted(request) -> bool:
        attempts = request.session.get(TwoFactorLoginChallengeService.SESSION_ATTEMPTS_KEY, 0)
        return attempts >= TwoFactorLoginChallengeService.MAX_ATTEMPTS

    @staticmethod
    def clear(request) -> None:
        for key in (
            TwoFactorLoginChallengeService.SESSION_USER_KEY,
            TwoFactorLoginChallengeService.SESSION_NEXT_KEY,
            TwoFactorLoginChallengeService.SESSION_ATTEMPTS_KEY,
            TwoFactorLoginChallengeService.SESSION_BACKEND_KEY,
            TwoFactorLoginChallengeService.SESSION_LAST_SENT_AT_KEY,
        ):
            request.session.pop(key, None)
        request.session.modified = True
