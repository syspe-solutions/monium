import logging

from apps.audit.loggers.base_logger import BaseLogger


class CeleryLogger(BaseLogger):
    def __init__(self):
        super().__init__("celery")

    def log_event(
        self,
        *,
        task_name: str,
        task_id: str,
        status: str,
        execution_time_ms: float = 0.0,
        error: str = "",
    ) -> None:
        payload = {
            "task_name": task_name,
            "task_id": task_id,
            "status": status,
            "execution_time_ms": execution_time_ms,
            "error": error,
        }

        level = logging.ERROR if status == "failed" else logging.INFO

        self._log(level, f"Celery task {task_name}", payload)
