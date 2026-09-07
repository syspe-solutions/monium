from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.inventory.models import Category
from apps.organizations.models import (
    Membership,
    MembershipRole,
    Organization,
    OrganizationGoal,
    OrganizationIndustry,
    OrganizationSize,
)

User = get_user_model()


class CategoryUsefulLifeUpdateViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Eletrônicos", slug="eletronicos-view")
        self.organization = Organization.objects.create(
            name="Org View", slug="org-view",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        self.url = reverse("inventory:category_useful_life_update", args=[self.category.id])

    def _login_with_role(self, role):
        user = User.objects.create_user(
            username=f"user-{role}", email=f"{role}@example.com", password="12345",
        )
        Membership.objects.create(organization=self.organization, user=user, role=role)
        self.client.force_login(user)
        return user

    def test_operator_can_set_useful_life(self):
        self._login_with_role(MembershipRole.OPERATOR)
        response = self.client.post(self.url, {"useful_life_months": "48"})

        self.assertRedirects(response, reverse("inventory:dashboard"))
        self.category.refresh_from_db()
        self.assertEqual(self.category.useful_life_months, 48)

    def test_viewer_cannot_set_useful_life(self):
        self._login_with_role(MembershipRole.VIEWER)
        response = self.client.post(self.url, {"useful_life_months": "48"})

        self.assertEqual(response.status_code, 403)
        self.category.refresh_from_db()
        self.assertIsNone(self.category.useful_life_months)

    def test_invalid_value_is_rejected(self):
        self._login_with_role(MembershipRole.OPERATOR)
        response = self.client.post(self.url, {"useful_life_months": "-5"})

        self.assertRedirects(response, reverse("inventory:dashboard"))
        self.category.refresh_from_db()
        self.assertIsNone(self.category.useful_life_months)
