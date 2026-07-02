import logging
from typing import Any, Dict, Optional
from apps.audit.dtos import ErrorType
from apps.audit.loggers.base_logger import BaseLogger


class ErrorLogger(BaseLogger):
    _instance = None

    @classmethod
    def _get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__("django")

    @classmethod
    def log_event(
        cls,
        *,
        error_type: ErrorType,
        message: str,
        stack_trace: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        instance = cls._get_instance()
        payload = {
            "error_type": error_type.value if isinstance(error_type, ErrorType) else error_type,
            "message": message,
            "stack_trace": stack_trace,
            "context": context or {},
        }

        instance._log(logging.ERROR, f"Application error {error_type.value if isinstance(error_type, ErrorType) else error_type}", payload)