from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.account.models import User
from apps.account.services.image_service import ImageService
from apps.common.utils import CommonUtils
from apps.organizations.models import Membership, MembershipRole, Organization


def give_organization(user):
    """Provisiona uma Organization pro usuário, como o onboarding faria — necessário
    porque RequireOrganizationMiddleware bloqueia usuários sem organização."""
    organization = Organization.objects.create(
        name=user.username, slug=f"org-{user.username}",
        industry="technology", size="1-10", primary_goal="it_equipment",
    )
    Membership.objects.create(organization=organization, user=user, role=MembershipRole.OWNER)
    return organization


class RegisterViewTests(TestCase):
    def test_register_page_loads_successfully(self):
        response = self.client.get(reverse("account:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/auth/register.html")

    def test_register_creates_user(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Strong@Password123",
            "confirm_password": "Strong@Password123",
        }
        response = self.client.post(reverse("account:register"), data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("account:login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_fails_with_mismatched_passwords(self):
        data = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "Strong@Password123",
            "confirm_password": "WrongPassword456",
        }
        response = self.client.post(reverse("account:register"), data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertIn('As senhas não coincidem.', form.errors['__all__'])
        self.assertFalse(User.objects.filter(username="user2").exists())

    def test_register_fails_with_invalid_password_size(self):
        data = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "J@2",
            "confirm_password": "J@2",
        }
        response = self.client.post(reverse("account:register"), data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertIn("password", form.errors)
        self.assertFalse(User.objects.filter(username="user2").exists())

    def test_register_fails_with_invalid_password_without_special_char(self):
        data = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "J2323",
            "confirm_password": "J2323",
        }
        response = self.client.post(reverse("account:register"), data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertIn("password", form.errors)
        self.assertFalse(User.objects.filter(username="user2").exists())


class UserLoginViewTests(TestCase):
    def setUp(self):
        CommonUtils().disable_welcome_signal()
        self.user = User.objects.create_user(
            username="testuser", password="12345")
        give_organization(self.user)

    def test_login_page_loads_successfully(self):
        response = self.client.get(reverse("account:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/auth/login.html")

    def test_valid_login_redirects_to_home(self):
        response = self.client.post(
            reverse("account:login"), {
                "username": "testuser", "password": "12345"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("inventory:home"))

    def test_authenticated_user_is_redirected(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("account:login"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("inventory:home"))


class LogoutViewTests(TestCase):
    def setUp(self):
        CommonUtils().disable_welcome_signal()
        self.user = User.objects.create_user(
            username="logoutuser", password="12345")
        give_organization(self.user)

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("account:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("account:login"))


class AuthenticatedTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = self._create_user()
        self.client.force_login(self.user)

    def _create_user(self):
        User = get_user_model()

        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="strong-pass"
        )
        give_organization(user)
        return user


class UploadAvatarViewTests(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("account:upload_avatar")
        self.image = ImageService.create_image()

    def _upload(self, file):
        return self.client.post(
            self.url,
            {"image": file}
        )

    @patch("apps.account.views.upload_avatar_view.ImageProcessor")
    def test_upload_avatar_success(self, MockProcessor):
        mock_processor_instance = MockProcessor.return_value
        mock_processor_instance.resize.return_value = self.image

        response = self._upload(self.image)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("account:profile_edit"))
        
        # Verify profile has avatar
        from apps.account.models import UserProfile
        profile = UserProfile.objects.get(user=self.user)
        self.assertTrue(profile.avatar)
        self.assertTrue(mock_processor_instance.resize.called)

    def test_upload_avatar_rejects_invalid_extension(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        invalid_file = SimpleUploadedFile(
            "virus.exe",
            b"malicious-content",
            content_type="application/octet-stream"
        )

        response = self._upload(invalid_file)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("account:profile_edit"))
        
        # Verify error message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Invalid image extension" in str(m) for m in messages))

    def test_upload_requires_authentication(self):
        self.client.logout()
        response = self._upload(self.image)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account:login"), response.url)
