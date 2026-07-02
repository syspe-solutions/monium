import logging
from typing import Any, Dict, Optional
from apps.audit.dtos import DatabaseAction
from apps.audit.loggers.base_logger import BaseLogger


class DatabaseLogger(BaseLogger):
    _instance = None

    @classmethod
    def _get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__("django.db.backends")

    @classmethod
    def log_event(
        cls,
        *,
        action: DatabaseAction,
        query: str,
        execution_time_ms: float,
        status: str,
        database_name: str,
        error: str = "",
    ) -> None:
        instance = cls._get_instance()
        payload = {
            "action": action.value if isinstance(action, DatabaseAction) else action,
            "query": query,
            "execution_time_ms": execution_time_ms,
            "status": status,
            "database_name": database_name,
            "error": error,
        }

        level = logging.ERROR if status == "failed" else logging.INFO

        instance._log(level, f"Database event: {action.value if isinstance(action, DatabaseAction) else action}", payload)
