import functools
import json
import logging
import re
import time
from datetime import datetime
from typing import Any, Dict, Final, Set

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from core.utilities.logging_context import get_request_context

DEFAULT_SENSITIVE_KEYS: Final[Set[str]] = {
    "password", "token", "secret", "key", "api_key", "card_number", 
    "auth", "authorization", "cookie", "set-cookie", "csrfmiddlewaretoken",
    "cpf", "email", "phone", "document"
}

class DataSanitizer:
    def __init__(self, sensitive_keys: Set[str] = DEFAULT_SENSITIVE_KEYS):
        self._pattern = re.compile(
            r'|'.join([rf'\b{re.escape(k)}\b' for k in sensitive_keys]), 
            re.IGNORECASE
        )
        self._placeholder: Final[str] = "[REDACTED]"

    def scrub(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                key: self._placeholder if self._pattern.search(str(key)) else self.scrub(value)
                for key, value in data.items()
            }
        
        if isinstance(data, list):
            return [self.scrub(item) for item in data]
        
        if isinstance(data, str):
            return self._placeholder if self._pattern.search(data) else data
            
        return data

def mask_sensitive_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Utility to mask sensitive data in a dictionary."""
    return DataSanitizer().scrub(payload)


class LogContextAdapter:
    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        context = get_request_context()
        return {
            "trace_id": context.get("trace_id"),
            "user_id": context.get("user_id"),
            "request": {
                "ip": context.get("ip_address"),
                "path": context.get("path"),
                "method": context.get("method"),
            }
        }


class StructuredJSONFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sanitizer = DataSanitizer()

    def format(self, record: logging.LogRecord) -> str:
        context_metadata = LogContextAdapter.get_metadata()
        
        log_payload: Dict[str, Any] = {
            "timestamp": self._get_iso_timestamp(record.created),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "context": context_metadata,
            "runtime": {
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "process": record.process,
                "thread": record.threadName
            }
        }

        extra_data = getattr(record, "extra_data", {})
        if extra_data:
            log_payload["data"] = self._sanitizer.scrub(extra_data)

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload, default=str)

    @staticmethod
    def _get_iso_timestamp(created_time: float) -> str:
        return datetime.fromtimestamp(created_time).isoformat() + "Z"


def trace_performance(logger_name: str = "performance"):
    def decorator(func):
        logger = logging.getLogger(logger_name)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.perf_counter() - start_time
                logger.info(
                    f"Performance trace: {func.__name__}",
                    extra={"extra_data": {
                        "function": func.__name__,
                        "duration_sec": round(duration, 4),
                        "status": "success"
                    }}
                )
        return wrapper
    return decorator


class WebSocketHandler(logging.Handler):
    def emit(self, record):
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                if not self.formatter:
                    self.formatter = StructuredJSONFormatter()
                
                log_entry = self.format(record)
                async_to_sync(channel_layer.group_send)(
                    "log_broadcast",
                    {
                        "type": "log_message",
                        "message": log_entry,
                    }
                )
        except Exception:
            # Silently fail to avoid recursion if channel layer fails
            pass

