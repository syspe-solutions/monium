from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse

from apps.setup.middleware import SetupRequiredMiddleware
from apps.setup.web.views.admin_setup_view import AdminSetupView


@override_settings(DATABASE_SETUP_REQUIRED=False)
class AdminSetupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.url = reverse("setup:admin")
        SetupRequiredMiddleware._superuser_exists = False
        # Essa view só existe enquanto não há nenhum superusuário — a suíte
        # inteira roda com um de baseline (core/test_runner.py), então partimos
        # daqui sem ele.
        get_user_model().objects.filter(is_superuser=True).delete()

    def test_guard_returns_404_when_database_still_not_configured(self):
        # Client() passaria pelo SetupRequiredMiddleware, que já intercepta antes
        # da view (coberto em test_middleware.py) — aqui testamos a guarda da
        # própria view isoladamente, chamando-a direto via RequestFactory.
        with override_settings(DATABASE_SETUP_REQUIRED=True):
            request = self.factory.get(self.url)
            with self.assertRaises(Http404):
                AdminSetupView.as_view()(request)

    def test_guard_returns_404_once_a_superuser_already_exists(self):
        get_user_model().objects.create_superuser(
            username="existing", email="existing@example.com", password="Strong@Password123"
        )
        request = self.factory.get(self.url)
        with self.assertRaises(Http404):
            AdminSetupView.as_view()(request)

    def test_creates_first_superuser_and_logs_in(self):
        response = self.client.post(self.url, {
            "username": "admin",
            "email": "admin@example.com",
            "password": "Strong@Password123",
            "confirm_password": "Strong@Password123",
        })

        self.assertRedirects(response, reverse("inventory:home"), fetch_redirect_response=False)

        user = get_user_model().objects.get(username="admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_password_mismatch_is_rejected(self):
        response = self.client.post(self.url, {
            "username": "admin",
            "email": "admin@example.com",
            "password": "Strong@Password123",
            "confirm_password": "Different@Password456",
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(get_user_model().objects.filter(username="admin").exists())

    def test_short_password_shows_length_error_not_mismatch_error(self):
        # clean_password() rejeita a senha curta e some com "password" de
        # cleaned_data — clean() não pode comparar isso com confirm_password
        # e disparar "as senhas não coincidem" por cima do erro real.
        response = self.client.post(self.url, {
            "username": "admin",
            "email": "admin@example.com",
            "password": "abc123",
            "confirm_password": "abc123",
        })

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("password", form.errors)
        self.assertNotIn("__all__", form.errors)
