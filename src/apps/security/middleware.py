
from django.http import JsonResponse

from apps.security.services import ExponentialBanService, WebSocketOriginService


class ExponentialBanMiddleware:
    LOGIN_URLS = ["/account/login/"]
    RESET_URLS = [
        "/account/reset/",
        "/account/reset/verify/",
        "/api/v1/auth/reset/",
        "/api/v1/auth/reset/verify/",
    ]

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST":
            ban_key = None

            if request.path in self.LOGIN_URLS:
                ban_key = request.POST.get("cpf")
            elif request.path in self.RESET_URLS:
                # /reset/ sends cpf; /reset/verify/ uses session user_id
                ban_key = request.POST.get("cpf") or request.session.get(
                    "password_reset_user_id"
                )

            if ban_key:
                remaining = ExponentialBanService.get_ban_remaining(ban_key)
                if remaining > 0:
                    return JsonResponse(
                        {"detail": f"Bloqueado por {remaining} segundos. Tente novamente mais tarde."},
                        status=429,
                    )

        return self.get_response(request)


class WsAllowedOriginValidator:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "websocket":
            return await self.app(scope, receive, send)

        headers = {
            key.decode().lower(): value.decode()
            for key, value in scope.get("headers", [])
        }

        origin = headers.get("origin")

        if not WebSocketOriginService.is_allowed(origin):
            await send({
                "type": "websocket.close",
                "code": 4003,
            })
            return

        return await self.app(scope, receive, send)
