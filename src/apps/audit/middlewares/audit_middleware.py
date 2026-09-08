import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse
from python_ipware import IpWare

from core.utilities.logging_context import clear_request_context, set_request_context

ipw = IpWare(precedence=("X_FORWARDED_FOR", "HTTP_X_FORWARDED_FOR"))

class AuditMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        
        ip, _ = ipw.get_client_ip(meta=request.META)
        ip_str = str(ip) if ip else request.META.get('REMOTE_ADDR')

        set_request_context(
            user_id=None,
            ip_address=ip_str,
            user_agent=request.headers.get("User-Agent"),
            trace_id=trace_id,
            path=request.path,
            method=request.method,
        )

        try:
            response = self.get_response(request)
            user_id = None
            
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = request.user.id
            
            set_request_context(
                user_id=user_id,
                ip_address=ip_str,
                user_agent=request.headers.get("User-Agent"),
                trace_id=trace_id,
                path=request.path,
                method=request.method,
            )
            
            response["X-Trace-ID"] = trace_id
            return response
        finally:
            clear_request_context()
