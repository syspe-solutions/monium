from time import perf_counter

from python_ipware import IpWare

from apps.audit.dtos import ErrorType, SecurityAction, SecurityStatus
from apps.audit.loggers.access_logger import AccessLogger
from apps.audit.loggers.error_logger import ErrorLogger
from apps.audit.loggers.security_logger import SecurityLogger

ipw = IpWare(precedence=("X_FORWARDED_FOR", "HTTP_X_FORWARDED_FOR"))

IGNORED_PREFIXES = ("/static/", "/media/")


class ProjectViewLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(IGNORED_PREFIXES):
            return self.get_response(request)

        started_at = perf_counter()
        response = self.get_response(request)
        elapsed_ms = round((perf_counter() - started_at) * 1000, 2)
        ip, _ = ipw.get_client_ip(meta=request.META)

        AccessLogger().log_event(
            method=request.method,
            endpoint=request.path,
            status_code=response.status_code,
            ip_address=str(ip) if ip else request.META.get("REMOTE_ADDR", ""),
            response_time_ms=elapsed_ms,
            user_agent=request.headers.get("User-Agent", ""),
            metadata={"querystring": request.META.get("QUERY_STRING", "")},
        )

        if response.status_code in {401, 403, 429}:
            SecurityLogger.log_event(
                user=getattr(request, "user", None),
                ip_address=str(ip) if ip else request.META.get("REMOTE_ADDR", ""),
                action="request_denied",
                status="denied",
                reason=f"http_{response.status_code}",
                user_agent=request.headers.get("User-Agent", ""),
            )

        if response.status_code >= 500:
            ErrorLogger.log_event(
                error_type=ErrorType.HTTP_SERVER_ERROR,
                message=f"{request.method} {request.path} -> {response.status_code}",
                context={
                    "endpoint": request.path,
                    "method": request.method,
                    "status_code": response.status_code,
                },
            )

        return response
