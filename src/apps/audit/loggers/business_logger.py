import logging
from typing import Any, Dict, Optional
from apps.audit.dtos import BusinessAction
from apps.audit.loggers.base_logger import BaseLogger


class BusinessLogger(BaseLogger):
    _instance = None

    @classmethod
    def _get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__("business")

    @classmethod
    def log_event(
        cls,
        *,
        user: Any,
        action: BusinessAction,
        entity: str,
        entity_id: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        level: int = logging.INFO,
    ) -> None:
        instance = cls._get_instance()
        payload = {
            "user": instance._normalize_user(user),
            "action": action.value if isinstance(action, BusinessAction) else action,
            "entity": entity,
            "entity_id": str(entity_id) if entity_id is not None else "",
            "details": details or {},
        }

        instance._log(level, f"Business event {action.value if isinstance(action, BusinessAction) else action}", payload)

