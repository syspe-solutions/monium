import json
import os
import tempfile
from datetime import timedelta

from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from apps.audit.services import LogReaderService


@override_settings(LOG_DIR_WEB=tempfile.gettempdir())
class FileMetricsStoreTests(SimpleTestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.override = override_settings(LOG_DIR_WEB=self.temp_dir.name)
        self.override.enable()
        self.addCleanup(self.override.disable)

        self.log_file = os.path.join(self.temp_dir.name, "business.log")
        self.snapshot_file = os.path.join(self.temp_dir.name, "metrics_snapshot.json")

    def _write_entries(self, entries):
        with open(self.log_file, "w", encoding="utf-8") as fh:
            for entry in entries:
                fh.write(json.dumps(entry) + "\n")

    def test_get_metrics_from_file_snapshot(self):
        now = timezone.now()
        minute = now.replace(second=0, microsecond=0).isoformat().replace("+00:00", "Z")
        previous = (now - timedelta(minutes=2)).replace(second=0, microsecond=0).isoformat().replace("+00:00", "Z")

        self._write_entries(
            [
                {"timestamp": minute, "level": "INFO", "message": "ok"},
                {"timestamp": minute, "level": "ERROR", "message": "boom"},
                {"timestamp": previous, "level": "CRITICAL", "message": "critical old"},
            ]
        )

        metrics = LogReaderService.get_metrics("business")
        self.assertEqual(metrics["total_count"], 3)
        self.assertEqual(metrics["critical_incidents"], 1)
        self.assertEqual(metrics["requests_per_minute"], 2)
        self.assertEqual(metrics["error_rate"], "33.33%")
        self.assertTrue(os.path.exists(self.snapshot_file))

    def test_incremental_refresh_does_not_duplicate(self):
        now = timezone.now().replace(second=0, microsecond=0).isoformat().replace("+00:00", "Z")
        self._write_entries([{"timestamp": now, "level": "INFO", "message": "a"}])

        first = LogReaderService.get_metrics("business")
        second = LogReaderService.get_metrics("business")

        self.assertEqual(first["total_count"], 1)
        self.assertEqual(second["total_count"], 1)

    def test_rotation_or_truncation_rebuilds_state(self):
        now = timezone.now().replace(second=0, microsecond=0).isoformat().replace("+00:00", "Z")
        # Primeiro arquivo: entrada grande para garantir file_offset alto
        self._write_entries([{"timestamp": now, "level": "INFO", "message": "x" * 200}])
        first = LogReaderService.get_metrics("business")
        self.assertEqual(first["total_count"], 1)

        # Simula truncagem: reescreve com conteúdo menor que o offset salvo
        # (garante detecção mesmo em sistemas sem suporte a inode, como NTFS/WSL)
        self._write_entries([{"timestamp": now, "level": "ERROR", "message": "new"}])
        second = LogReaderService.get_metrics("business")
        self.assertEqual(second["total_count"], 1)
        self.assertEqual(second["error_rate"], "100.00%")

    def test_read_logs_returns_latest_entries(self):
        now = timezone.now().replace(second=0, microsecond=0).isoformat().replace("+00:00", "Z")
        self._write_entries(
            [
                {"timestamp": now, "level": "INFO", "message": "first"},
                {"timestamp": now, "level": "INFO", "message": "second"},
                {"timestamp": now, "level": "ERROR", "message": "third"},
            ]
        )

        logs = LogReaderService.read_logs("business", limit=2, filters={})
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]["message"], "third")
        self.assertEqual(logs[1]["message"], "second")

    def tearDown(self):
        if os.path.exists(self.snapshot_file):
            os.unlink(self.snapshot_file)
