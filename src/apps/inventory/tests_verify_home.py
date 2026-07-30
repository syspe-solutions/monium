from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.inventory.models import Acquisition, Category, Imovel, ImovelCategory, Movel, Sector
from apps.organizations.models import (
    Membership,
    MembershipRole,
    Organization,
    OrganizationGoal,
    OrganizationIndustry,
    OrganizationSize,
)


class HomeAndLayoutSmokeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester2", email="tester2@example.com", password="StrongPass123!"
        )
        self.organization = Organization.objects.create(
            name="Org Verify",
            slug="org-verify",
            industry=OrganizationIndustry.values[0],
            size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        Membership.objects.create(organization=self.organization, user=self.user, role=MembershipRole.OWNER)
        self.category = Category.objects.create(name="Eletronicos", slug="eletronicos")
        self.sector = Sector.objects.create(name="TI", slug="ti")
        self.imovel_category = ImovelCategory.objects.create(name="Sede", slug="sede")

        movel = Movel.objects.create(
            organization=self.organization,
            code="PAT-0001",
            name="Notebook Dell",
            category=self.category,
            sector=self.sector,
        )
        Acquisition.objects.create(item=movel, value=Decimal("4500.00"), purchase_date=date.today())

        movel_no_value = Movel.objects.create(
            organization=self.organization,
            code="PAT-0002",
            name="Cadeira",
            category=self.category,
            sector=self.sector,
        )

        imovel = Imovel.objects.create(
            organization=self.organization,
            code="IM-0001",
            name="Sala Comercial",
            category=self.imovel_category,
        )
        Acquisition.objects.create(item=imovel, value=Decimal("150000.00"), purchase_date=date.today())

        self.client.force_login(self.user)

    def test_home_page_renders_with_wallet_panel(self):
        response = self.client.get(reverse("inventory:home"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Minha Carteira", content)
        self.assertIn("Bens com Maior Valor", content)
        self.assertIn("Valor do Acervo por Período", content)
        self.assertIn("R$ 154.500,00", content)  # 4500 + 150000 total
        self.assertIn("main-sidebar", content)  # aside restored

    def test_home_page_renders_with_no_valued_items(self):
        Acquisition.objects.all().delete()
        response = self.client.get(reverse("inventory:home"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("R$ 0,00", content)
        self.assertIn("Nenhum bem com valor cadastrado ainda.", content)
        self.assertIn("Nenhum valor de aquisição registrado neste período ainda.", content)

    def test_patrimonio_list_renders_with_aside(self):
        response = self.client.get(reverse("inventory:patrimonio_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("main-sidebar", response.content.decode())

    def test_organizations_settings_renders_with_aside(self):
        response = self.client.get(reverse("organizations:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("main-sidebar", response.content.decode())
