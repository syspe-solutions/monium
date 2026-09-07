from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.inventory.models import Category, Sector
from apps.organizations.models import Membership, MembershipRole, Organization

User = get_user_model()


def create_organization(user, industry="technology"):
    organization = Organization.objects.create(
        name="Test Org", slug=f"test-org-{user.username}",
        industry=industry, size="1-10", primary_goal="it_equipment",
    )
    Membership.objects.create(organization=organization, user=user, role=MembershipRole.OWNER)
    return organization


class OrganizationOnboardingViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="12345")
        self.organization = create_organization(self.user, industry="technology")
        self.client.force_login(self.user)
        session = self.client.session
        session["active_organization_id"] = str(self.organization.id)
        session.save()

    def test_onboarding_page_loads_with_suggestions(self):
        response = self.client.get(reverse("organizations:onboarding"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "organizations/onboarding.html")
        self.assertContains(response, "Equipamentos de Informática")

    def test_existing_category_is_marked_as_already_available(self):
        Category.objects.create(name="Equipamentos de Informática", slug="equipamentos-de-informatica")

        response = self.client.get(reverse("organizations:onboarding"))

        self.assertNotContains(response, 'name="categories" value="Equipamentos de Informática"')
        self.assertContains(response, "Equipamentos de Informática")

    def test_post_creates_selected_categories_and_sectors(self):
        response = self.client.post(reverse("organizations:onboarding"), {
            "categories": ["Equipamentos de Informática", "Telecomunicações"],
            "sectors": ["Tecnologia da Informação"],
        })

        self.assertRedirects(response, reverse("inventory:home"))
        self.assertTrue(Category.objects.filter(name="Equipamentos de Informática").exists())
        self.assertTrue(Category.objects.filter(name="Telecomunicações").exists())
        self.assertTrue(Sector.objects.filter(name="Tecnologia da Informação").exists())

    def test_post_does_not_duplicate_existing_categories(self):
        Category.objects.create(name="Equipamentos de Informática", slug="equipamentos-de-informatica")

        self.client.post(reverse("organizations:onboarding"), {
            "categories": ["Equipamentos de Informática"],
        })

        self.assertEqual(Category.objects.filter(name="Equipamentos de Informática").count(), 1)

    def test_post_without_selection_still_redirects(self):
        response = self.client.post(reverse("organizations:onboarding"), {})
        self.assertRedirects(response, reverse("inventory:home"))
