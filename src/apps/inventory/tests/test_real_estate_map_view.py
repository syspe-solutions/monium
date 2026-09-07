from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.inventory.models import RealEstateAsset, RealEstateCategory
from apps.organizations.models import (
    Membership,
    MembershipRole,
    Organization,
    OrganizationGoal,
    OrganizationIndustry,
    OrganizationSize,
)


class RealEstateMapViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="map-tester", email="map-tester@example.com", password="StrongPass123!"
        )
        self.organization = Organization.objects.create(
            name="Org Map",
            slug="org-map",
            industry=OrganizationIndustry.values[0],
            size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        Membership.objects.create(organization=self.organization, user=self.user, role=MembershipRole.OWNER)
        self.category = RealEstateCategory.objects.create(name="Sede", slug="sede")
        self.client.force_login(self.user)

    def test_shows_empty_state_when_no_real_estate_exists(self):
        response = self.client.get(reverse("inventory:real_estate_map"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Nenhum imóvel tem coordenadas cadastradas ainda.", response.content.decode())

    def test_warns_about_properties_without_coordinates(self):
        RealEstateAsset.objects.create(
            organization=self.organization, code="IM-0001", name="Sem coordenadas", category=self.category
        )
        response = self.client.get(reverse("inventory:real_estate_map"))
        content = response.content.decode()
        self.assertIn("imóvel não tem coordenadas e não aparece no mapa", content)
        self.assertIn("Nenhum imóvel tem coordenadas cadastradas ainda.", content)

    def test_renders_map_with_property_pin(self):
        real_estate = RealEstateAsset.objects.create(
            organization=self.organization,
            code="IM-0002",
            name="Sede <script>",
            address="Rua Um, 100",
            category=self.category,
            latitude=Decimal("-23.550520"),
            longitude=Decimal("-46.633308"),
        )
        response = self.client.get(reverse("inventory:real_estate_map"))
        content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn('id="real-estate-map"', content)
        self.assertIn("-23.55052", content)
        self.assertIn(reverse("inventory:real_estate_detail", args=[real_estate.id]), content)
        # Nome do imóvel deve chegar escapado no payload JSON (json_script escapa
        # "<"/">"), nunca como HTML cru — confirma que não há brecha de XSS aqui.
        self.assertNotIn("Sede <script>", content)
        self.assertIn("\\u003Cscript\\u003E", content)

    def test_map_scoped_to_organization(self):
        other_org = Organization.objects.create(
            name="Outra Org",
            slug="outra-org",
            industry=OrganizationIndustry.values[0],
            size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        other_category = RealEstateCategory.objects.create(name="Outra Categoria", slug="outra-categoria")
        RealEstateAsset.objects.create(
            organization=other_org,
            code="IM-9999",
            name="Não deveria aparecer",
            category=other_category,
            latitude=Decimal("1.0"),
            longitude=Decimal("1.0"),
        )
        response = self.client.get(reverse("inventory:real_estate_map"))
        self.assertNotIn("Não deveria aparecer", response.content.decode())
