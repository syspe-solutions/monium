import logging
from typing import Any, Dict


class BaseLogger:
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
        
    def _normalize_user(self, user_obj) -> str:
        if not user_obj or getattr(user_obj, "is_anonymous", True):
            return "anonymous"
        if hasattr(user_obj, "get_username"):
            return str(user_obj.get_username())
        return str(getattr(user_obj, "id", "authenticated"))

    def _log(self, level: int, message: str, payload: Dict[str, Any]) -> None:
        self.logger.log(level, message, extra={"extra_data": payload})
