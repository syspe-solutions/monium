import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse

from apps.setup.dtos.database_configuration_dto import DatabaseConfigurationDTO
from apps.setup.middleware import SetupRequiredMiddleware
from apps.setup.services.database_connection_tester_service import DatabaseConnectionTestError
from apps.setup.services.runtime_database_config_service import RuntimeDatabaseConfigService
from apps.setup.web.views.database_setup_view import DatabaseSetupView


class DatabaseSetupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.url = reverse("setup:database")
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp_dir, ignore_errors=True)
        SetupRequiredMiddleware._superuser_exists = False

    def _override(self, **extra):
        return override_settings(
            DATABASE_SETUP_REQUIRED=True,
            APP_DATA_DIR=self.tmp_dir,
            RUNTIME_DB_CONFIG_PATH=self.tmp_dir / "database.env",
            **extra,
        )

    def test_guard_returns_404_once_database_is_already_configured(self):
        # Client() passaria pelo SetupRequiredMiddleware, que já intercepta antes
        # da view (coberto em test_middleware.py) — aqui testamos a guarda da
        # própria view isoladamente, chamando-a direto via RequestFactory.
        with override_settings(DATABASE_SETUP_REQUIRED=False):
            request = self.factory.get(self.url)
            with self.assertRaises(Http404):
                DatabaseSetupView.as_view()(request)

    def test_reachable_when_database_configured_but_no_admin_yet(self):
        # Volta do passo 2 (admin ainda não criado) pro passo 1 pra revisar o banco.
        get_user_model().objects.filter(is_superuser=True).delete()
        with override_settings(DATABASE_SETUP_REQUIRED=False):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_prefills_form_with_previously_persisted_non_secret_fields(self):
        with self._override():
            RuntimeDatabaseConfigService().persist(DatabaseConfigurationDTO(
                engine="postgresql", host="db.example.com", port="5433",
                name="monium", user="monium", password="secret",
            ))
            response = self.client.get(self.url)

        self.assertEqual(response.context["form"].initial["host"], "db.example.com")
        self.assertEqual(response.context["form"].initial["port"], "5433")
        self.assertNotIn("password", response.context["form"].initial)

    def test_choosing_sqlite_completes_setup_without_restart(self):
        with self._override():
            response = self.client.post(self.url, {"engine": "sqlite3"})

            self.assertRedirects(response, reverse("setup:admin"), fetch_redirect_response=False)
            self.assertFalse(settings.DATABASE_SETUP_REQUIRED)

        config_content = (self.tmp_dir / "database.env").read_text()
        self.assertIn("DB_ENGINE=sqlite3", config_content)

    def test_postgresql_requires_all_connection_fields(self):
        with self._override():
            response = self.client.post(self.url, {"engine": "postgresql", "host": "db.example.com"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertFalse((self.tmp_dir / "database.env").exists())

    def test_postgresql_connection_failure_does_not_persist_or_restart(self):
        with self._override(), \
             patch(
                 "apps.setup.web.views.database_setup_view.DatabaseConnectionTesterService.test",
                 side_effect=DatabaseConnectionTestError("boom"),
             ), \
             patch("apps.setup.web.views.database_setup_view.ServerRestartService.schedule_restart") as schedule_restart:
            response = self.client.post(self.url, {
                "engine": "postgresql",
                "host": "db.example.com",
                "port": "5432",
                "name": "monium",
                "user": "monium",
                "password": "secret",
            })

        self.assertEqual(response.status_code, 200)
        self.assertIn("boom", str(response.context["form"].errors))
        self.assertFalse((self.tmp_dir / "database.env").exists())
        schedule_restart.assert_not_called()

    def test_postgresql_success_persists_config_and_schedules_restart(self):
        with self._override(), \
             patch("apps.setup.web.views.database_setup_view.DatabaseConnectionTesterService.test"), \
             patch("apps.setup.web.views.database_setup_view.ServerRestartService.schedule_restart") as schedule_restart:
            response = self.client.post(self.url, {
                "engine": "postgresql",
                "host": "db.example.com",
                "port": "5432",
                "name": "monium",
                "user": "monium",
                "password": "secret",
            })

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "setup/restarting.html")
            # A escolha de Postgres depende de um restart pra valer — o flag em
            # memória não muda sozinho (diferente do branch SQLite).
            self.assertTrue(settings.DATABASE_SETUP_REQUIRED)

        schedule_restart.assert_called_once()
        config_content = (self.tmp_dir / "database.env").read_text()
        self.assertIn("DB_ENGINE=postgresql", config_content)
        self.assertIn("DB_HOST=db.example.com", config_content)
