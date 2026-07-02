from time import time
from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone
from python_ipware import IpWare

from apps.audit.tasks import record_request_audit

ipw = IpWare(precedence=("X_FORWARDED_FOR", "HTTP_X_FORWARDED_FOR"))

class AuditorMiddleware:
    """
    Decoupled auditor middleware that logs to stdout and offloads DB persistence to Celery.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.AUDITOR_ENABLE = getattr(settings, "AUDITOR_MIDDLEWARE_ENABLE", False)

    def __call__(self, request):
        # Exclude static, media, audit dashboard and health check from audit
        if not self.AUDITOR_ENABLE or request.path.startswith(('/static/', '/media/', '/audit/', '/health/')):
            return self.get_response(request)

        start_time = time()
        previous_queries = connection.queries[::] if settings.DEBUG else []

        response = self.get_response(request)

        duration = time() - start_time
        
        # Calculate DB time if possible
        db_time = 0.0
        if settings.DEBUG:
            current_queries = connection.queries[len(previous_queries):]
            db_time = sum(float(q.get('time', 0)) for q in current_queries)
            queries_count = len(current_queries)
        else:
            # Fallback for production if connection.queries is not available
            queries_count = len(connection.queries) - len(previous_queries)
            # In production, without custom instrumentation, db_time might stay 0
            # or we could use another way to track it.
        
        python_time = duration - db_time
        
        ip, _ = ipw.get_client_ip(meta=request.META)

        audit_data = {
            "path": request.path,
            "method": request.method,
            "total_time": duration,
            "python_time": python_time,
            "db_time": db_time,
            "total_queries": queries_count,
            "ip": str(ip) if ip else "0.0.0.0",
            "response_status_code": response.status_code,
            "user_agent": request.headers.get("User-Agent"),
            "host": request.get_host().split(':')[0],
            "port": request.get_port(),
        }

        # Async persistence for request audit model
        transaction.on_commit(lambda: record_request_audit.delay(audit_data))

        return response
