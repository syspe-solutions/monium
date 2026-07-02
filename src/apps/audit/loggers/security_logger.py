import logging
from typing import Any
from apps.audit.dtos import SecurityAction, SecurityStatus
from apps.audit.loggers.base_logger import BaseLogger


class SecurityLogger(BaseLogger):
    _instance = None

    @classmethod
    def _get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__("security")

    @classmethod
    def log_event(
        cls,
        *,
        user: Any,
        ip_address: str,
        action: SecurityAction,
        status: SecurityStatus,
        reason: str = "",
        user_agent: str = "",
    ) -> None:
        instance = cls._get_instance()
        payload = {
            "user": instance._normalize_user(user),
            "ip_address": ip_address,
            "action": action.value if isinstance(action, SecurityAction) else action,
            "status": status.value if isinstance(status, SecurityStatus) else status,
            "reason": reason,
            "user_agent": user_agent,
        }

        level = logging.INFO if status == SecurityStatus.SUCCESS else logging.WARNING

        instance._log(level, f"Security event: {action.value if isinstance(action, SecurityAction) else action}", payload)