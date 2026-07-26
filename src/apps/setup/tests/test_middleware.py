from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.setup.middleware import SetupRequiredMiddleware


class SetupRequiredMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()
        SetupRequiredMiddleware._superuser_exists = False
        # A suíte inteira roda com um superusuário de baseline (core/test_runner.py),
        # senão todo teste de todo app seria redirecionado pro instalador. Aqui
        # testamos justamente os dois estados, então partimos de "nenhum" e cada
        # teste cria o que precisar.
        get_user_model().objects.filter(is_superuser=True).delete()

    @override_settings(DATABASE_SETUP_REQUIRED=True)
    def test_redirects_everything_to_database_step_when_db_not_configured(self):
        response = self.client.get(reverse("account:login"))
        self.assertRedirects(response, reverse("setup:database"), fetch_redirect_response=False)

    @override_settings(DATABASE_SETUP_REQUIRED=True)
    def test_database_step_itself_is_reachable_when_db_not_configured(self):
        response = self.client.get(reverse("setup:database"))
        self.assertEqual(response.status_code, 200)

    @override_settings(DATABASE_SETUP_REQUIRED=False)
    def test_redirects_everything_to_admin_step_when_no_superuser_exists(self):
        response = self.client.get(reverse("account:login"))
        self.assertRedirects(response, reverse("setup:admin"), fetch_redirect_response=False)

    @override_settings(DATABASE_SETUP_REQUIRED=False)
    def test_admin_step_itself_is_reachable_when_no_superuser_exists(self):
        response = self.client.get(reverse("setup:admin"))
        self.assertEqual(response.status_code, 200)

    @override_settings(DATABASE_SETUP_REQUIRED=False)
    def test_can_navigate_back_to_database_step_while_admin_is_pending(self):
        response = self.client.get(reverse("setup:database"))
        self.assertEqual(response.status_code, 200)

    @override_settings(DATABASE_SETUP_REQUIRED=True)
    def test_cannot_skip_ahead_to_admin_step_while_database_is_pending(self):
        response = self.client.get(reverse("setup:admin"))
        self.assertRedirects(response, reverse("setup:database"), fetch_redirect_response=False)

    @override_settings(DATABASE_SETUP_REQUIRED=False)
    def test_normal_navigation_once_setup_is_complete(self):
        get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="Strong@Password123"
        )
        response = self.client.get(reverse("account:login"))
        self.assertEqual(response.status_code, 200)

    @override_settings(DATABASE_SETUP_REQUIRED=False)
    def test_setup_urls_redirect_away_once_setup_is_complete(self):
        get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="Strong@Password123"
        )
        response = self.client.get(reverse("setup:database"))
        self.assertRedirects(response, reverse("account:login"), fetch_redirect_response=False)
