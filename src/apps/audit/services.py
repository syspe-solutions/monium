import json
import os
from typing import List, Dict, Optional, Any
from django.conf import settings
from core.utilities.structured_logging import mask_sensitive_data
from django.utils import timezone
from apps.audit.file_metrics import FileMetricsStore

class LogReaderService:
    LAYERS_MAP = {
        'business': 'business.log',
        'access': 'access.log',
        'security': 'security.log',
        'performance': 'performance.log',
        'error': 'error.log',
        'celery': 'celery.log',
        'database': 'database.log',
    }

    @classmethod
    def get_file_path(cls, layer: str) -> str:
        filename = cls.LAYERS_MAP.get(layer)
        if not filename:
             return ""
        return os.path.join(settings.LOG_DIR_WEB, filename)

    @classmethod
    def read_logs(cls, layer: str, limit: int = 100, filters: Optional[Dict] = None) -> List[Dict]:
        path = cls.get_file_path(layer)
        if not path or not os.path.exists(path):
            return []

        logs = []
        try:
            with open(path, "r", encoding="utf-8") as fh:
                entries = fh.readlines()

            for line in reversed(entries):
                if len(logs) >= limit:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if cls._apply_filters(entry, filters):
                    logs.append(mask_sensitive_data(entry))
        except Exception:
            pass
        
        return logs

    @staticmethod
    def _apply_filters(entry: Dict, filters: Optional[Dict]) -> bool:
        if not filters:
            return True
        
        level_filter = filters.get('level')
        if level_filter and entry.get('level', '').upper() != level_filter.upper():
            return False
        
        trace_id_filter = filters.get('trace_id')
        if trace_id_filter:
            context = entry.get('context', {})
            entry_trace_id = context.get('trace_id') or entry.get('trace_id')
            if entry_trace_id != trace_id_filter:
                return False

        # Text search
        query = filters.get('q')
        if query:
            message = str(entry.get('message', '')).lower()
            context_str = str(entry.get('context', '')).lower()
            query_lower = query.lower()
            if query_lower not in message and query_lower not in context_str:
                return False
            
        return True

    @classmethod
    def get_metrics(cls, layer: str) -> Dict[str, Any]:
        try:
            log_path = cls.get_file_path(layer)
            state = FileMetricsStore.refresh_layer(layer=layer, log_path=log_path)
            total_count = state.total
            error_count = state.levels.get("ERROR", 0)
            critical_count = state.levels.get("CRITICAL", 0)
            minute_ts = timezone.now().strftime("%Y%m%d%H%M")
            rpm = state.rpm_buckets.get(minute_ts, 0)

            error_rate = (error_count / total_count * 100) if total_count > 0 else 0

            return {
                "total_count": total_count,
                "error_rate": f"{error_rate:.2f}%",
                "critical_incidents": critical_count,
                "requests_per_minute": rpm,
                "layer": layer
            }
        except Exception:
            return {
                "total_count": 0,
                "error_rate": "0.00%",
                "critical_incidents": 0,
                "requests_per_minute": 0,
                "layer": layer
            }
