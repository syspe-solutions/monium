from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.organizations.models import Membership, MembershipRole, Organization

User = get_user_model()


class SettingsViewTest(TestCase):
    def test_settings_page_renders_for_logged_in_user(self):
        user = User.objects.create_user(username="settingsuser", password="x", email="s@s.com")
        organization = Organization.objects.create(name="Test Org")
        Membership.objects.create(user=user, organization=organization, role=MembershipRole.OWNER)
        self.client.force_login(user)
        response = self.client.get(reverse("account:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Language")
        self.assertContains(response, "Help & Support")

    def test_settings_page_requires_login(self):
        response = self.client.get(reverse("account:settings"))
        self.assertNotEqual(response.status_code, 200)

    def test_staff_user_sees_embedded_email_settings_section(self):
        user = User.objects.create_user(
            username="staffsettingsuser", password="x", email="staff@s.com", is_staff=True,
        )
        organization = Organization.objects.create(name="Staff Org")
        Membership.objects.create(user=user, organization=organization, role=MembershipRole.OWNER)
        self.client.force_login(user)
        response = self.client.get(reverse("account:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email settings")
        self.assertContains(response, reverse("settings:email_settings"))

    def test_non_staff_user_does_not_see_email_settings_section(self):
        user = User.objects.create_user(username="plainuser", password="x", email="plain@s.com")
        organization = Organization.objects.create(name="Plain Org")
        Membership.objects.create(user=user, organization=organization, role=MembershipRole.OWNER)
        self.client.force_login(user)
        response = self.client.get(reverse("account:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("settings:email_settings"))
