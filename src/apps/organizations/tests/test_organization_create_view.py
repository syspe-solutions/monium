from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class OrganizationCreateRedirectsToOnboardingTests(TestCase):
    def test_create_redirects_to_onboarding(self):
        user = User.objects.create_user(username="newowner", password="12345")
        self.client.force_login(user)

        response = self.client.post(reverse("organizations:create"), {
            "name": "My Org",
            "industry": "technology",
            "size": "1-10",
            "primary_goal": "it_equipment",
        })

        self.assertRedirects(response, reverse("organizations:onboarding"))
