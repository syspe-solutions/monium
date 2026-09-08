from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any, Dict

from django.conf import settings
from django.utils import timezone as dj_timezone

from apps.audit.constants import RPM_WINDOW_MINUTES
from apps.audit.dtos import LayerState


class FileMetricsStore:
    _lock = RLock()
    _snapshot_name = "metrics_snapshot.json"

    @classmethod
    def snapshot_path(cls) -> str:
        return os.path.join(settings.LOG_DIR_WEB, cls._snapshot_name)

    @classmethod
    def _empty_layer_state(cls) -> LayerState:
        return LayerState(
            total=0,
            levels={},
            rpm_buckets={},
            file_offset=0,
            file_inode=0,
            file_size=0,
        )

    @classmethod
    def _load_snapshot(cls) -> Dict[str, Any]:
        path = cls.snapshot_path()
        if not os.path.exists(path):
            return {"layers": {}}
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and isinstance(data.get("layers"), dict):
                return data
        except (OSError, json.JSONDecodeError):
            pass
        return {"layers": {}}

    @classmethod
    def _save_snapshot(cls, data: Dict[str, Any]) -> None:
        os.makedirs(settings.LOG_DIR_WEB, exist_ok=True)
        target_path = cls.snapshot_path()
        fd, tmp_path = tempfile.mkstemp(prefix="metrics_snapshot_", suffix=".json", dir=settings.LOG_DIR_WEB)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                json.dump(data, tmp, ensure_ascii=True, separators=(",", ":"))
            os.replace(tmp_path, target_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @classmethod
    def _serialize_layer_state(cls, state: LayerState) -> Dict[str, Any]:
        return {
            "total": state.total,
            "levels": state.levels,
            "rpm_buckets": state.rpm_buckets,
            "file_offset": state.file_offset,
            "file_inode": state.file_inode,
            "file_size": state.file_size,
        }

    @classmethod
    def _deserialize_layer_state(cls, raw: Dict[str, Any]) -> LayerState:
        state = cls._empty_layer_state()
        state.total = int(raw.get("total", 0))
        state.levels = {str(k).upper(): int(v) for k, v in dict(raw.get("levels", {})).items()}
        state.rpm_buckets = {str(k): int(v) for k, v in dict(raw.get("rpm_buckets", {})).items()}
        state.file_offset = int(raw.get("file_offset", 0))
        state.file_inode = int(raw.get("file_inode", 0))
        state.file_size = int(raw.get("file_size", 0))
        return state

    @classmethod
    def _parse_timestamp_to_minute(cls, timestamp_str: str | None) -> str | None:
        if not timestamp_str:
            return None
        try:
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            return dt.astimezone(timezone.utc).strftime("%Y%m%d%H%M")
        except ValueError:
            return None

    @classmethod
    def _prune_rpm_buckets(cls, buckets: Dict[str, int]) -> Dict[str, int]:
        cutoff = (dj_timezone.now() - timedelta(minutes=RPM_WINDOW_MINUTES)).astimezone(timezone.utc).strftime("%Y%m%d%H%M")
        return {k: v for k, v in buckets.items() if k >= cutoff}

    @classmethod
    def _accumulate_entry(cls, state: LayerState, entry: Dict[str, Any]) -> None:
        state.total += 1
        level = str(entry.get("level", "INFO")).upper()
        state.levels[level] = state.levels.get(level, 0) + 1

        minute = cls._parse_timestamp_to_minute(entry.get("timestamp"))
        if minute:
            state.rpm_buckets[minute] = state.rpm_buckets.get(minute, 0) + 1

    @classmethod
    def _rebuild_state_from_file(cls, log_path: str) -> LayerState:
        state = cls._empty_layer_state()
        if not os.path.exists(log_path):
            return state

        try:
            st = os.stat(log_path)
            state.file_inode = int(st.st_ino)
            state.file_size = int(st.st_size)
            state.file_offset = 0

            with open(log_path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    cls._accumulate_entry(state, entry)
                state.file_offset = fh.tell()
        except OSError:
            return cls._empty_layer_state()

        state.rpm_buckets = cls._prune_rpm_buckets(state.rpm_buckets)
        return state

    @classmethod
    def _update_state_incremental(cls, state: LayerState, log_path: str) -> LayerState:
        if not os.path.exists(log_path):
            return cls._empty_layer_state()

        try:
            st = os.stat(log_path)
        except OSError:
            return cls._empty_layer_state()

        inode = int(st.st_ino)
        size = int(st.st_size)
        rotated_or_truncated = state.file_inode != inode or size < state.file_offset
        if rotated_or_truncated:
            return cls._rebuild_state_from_file(log_path)

        try:
            with open(log_path, "r", encoding="utf-8") as fh:
                fh.seek(state.file_offset)
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    cls._accumulate_entry(state, entry)
                state.file_offset = fh.tell()
                state.file_size = size
                state.file_inode = inode
        except OSError:
            return cls._empty_layer_state()

        state.rpm_buckets = cls._prune_rpm_buckets(state.rpm_buckets)
        return state

    @classmethod
    def refresh_layer(cls, layer: str, log_path: str) -> LayerState:
        with cls._lock:
            snapshot = cls._load_snapshot()
            raw_state = snapshot["layers"].get(layer, {})
            state = cls._deserialize_layer_state(raw_state) if raw_state else cls._empty_layer_state()
            state = cls._update_state_incremental(state, log_path)
            snapshot["layers"][layer] = cls._serialize_layer_state(state)
            cls._save_snapshot(snapshot)
            return state

    @classmethod
    def rebuild_all(cls, layers_map: Dict[str, str]) -> int:
        with cls._lock:
            snapshot = {"layers": {}}
            processed = 0
            for layer, filename in layers_map.items():
                log_path = os.path.join(settings.LOG_DIR_WEB, filename)
                state = cls._rebuild_state_from_file(log_path)
                snapshot["layers"][layer] = cls._serialize_layer_state(state)
                processed += 1
            cls._save_snapshot(snapshot)
            return processed
