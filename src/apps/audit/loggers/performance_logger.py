import logging
from typing import Any, Dict, Optional
from apps.audit.dtos import PerformanceAction
from apps.audit.loggers.base_logger import BaseLogger


class PerformanceLogger(BaseLogger):
    _instance = None

    @classmethod
    def _get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__("performance")

    @classmethod
    def log_event(
        cls,
        *,
        action: PerformanceAction,
        function_name: str = "",
        endpoint: str = "",
        execution_time_ms: float = 0.0,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        instance = cls._get_instance()
        payload = {
            "action": action.value if isinstance(action, PerformanceAction) else action,
            "function_name": function_name,
            "endpoint": endpoint,
            "execution_time_ms": execution_time_ms,
            "status": status,
            "metadata": metadata or {},
        }

        instance._log(logging.INFO, f"Performance event: {action.value if isinstance(action, PerformanceAction) else action}", payload)

