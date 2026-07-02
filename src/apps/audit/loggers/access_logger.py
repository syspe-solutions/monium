import logging
from typing import Any, Dict, Optional
from apps.audit.loggers.base_logger import BaseLogger


class AccessLogger(BaseLogger):
    def __init__(self):
        super().__init__("django.request")

    def log_event(
        self,
        *,
        method: str,
        endpoint: str,
        status_code: int,
        ip_address: str,
        response_time_ms: float,
        user_agent: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        payload = {
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "ip_address": ip_address,
            "response_time_ms": response_time_ms,
            "user_agent": user_agent,
            "metadata": metadata or {},
        }

        self._log(
            logging.INFO,
            f"HTTP {method} {endpoint} -> {status_code}",
            payload,
        )
