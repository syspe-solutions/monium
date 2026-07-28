from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.inventory.models import Category, Imovel, ImovelCategory, Movel, Sector
from apps.organizations.models import (
    Membership,
    MembershipRole,
    Organization,
    OrganizationGoal,
    OrganizationIndustry,
    OrganizationSize,
)


class InventoryEditFlowTests(TestCase):
    """Cobertura da edição de itens/imóveis (antes inexistente: só havia create + detail)."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester", email="tester@example.com", password="StrongPass123!"
        )
        self.organization = Organization.objects.create(
            name="Org Teste",
            slug="org-teste",
            industry=OrganizationIndustry.values[0],
            size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        Membership.objects.create(organization=self.organization, user=self.user, role=MembershipRole.OWNER)
        self.category = Category.objects.create(name="Eletrônicos", slug="eletronicos")
        self.sector = Sector.objects.create(name="TI", slug="ti")
        self.imovel_category = ImovelCategory.objects.create(name="Sede", slug="sede")
        self.client.force_login(self.user)

    def _movel_payload(self, **overrides):
        payload = {
            "code": "PAT-0001",
            "name": "Notebook",
            "category": self.category.id,
            "sector": self.sector.id,
            "status": "em_uso",
            "condition": "bom",
            "ownership": "proprio",
            "brand_id": "",
        }
        payload.update(overrides)
        return payload

    def _imovel_payload(self, **overrides):
        payload = {
            "code": "IMV-0001",
            "name": "Sede Central",
            "category": self.imovel_category.id,
            "ownership": "proprio",
            "condition": "bom",
            "cartorio_situacao": "nao_registrado",
        }
        payload.update(overrides)
        return payload

    def test_movel_create_redirects_to_detail(self):
        response = self.client.post(reverse("inventory:item_create"), self._movel_payload())
        item = Movel.objects.get(code="PAT-0001")
        self.assertRedirects(response, reverse("inventory:item_detail", args=[item.id]))

    def test_movel_update_view_get_and_post(self):
        item = Movel.objects.create(
            organization=self.organization, code="PAT-0002", name="Mouse",
            category=self.category, sector=self.sector, status="em_uso",
        )

        get_response = self.client.get(reverse("inventory:item_update", args=[item.id]))
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, "Mouse")

        post_response = self.client.post(
            reverse("inventory:item_update", args=[item.id]),
            self._movel_payload(code="PAT-0002", name="Mouse sem fio", status="em_manutencao"),
        )
        item.refresh_from_db()
        self.assertEqual(item.name, "Mouse sem fio")
        self.assertEqual(item.status, "em_manutencao")
        self.assertRedirects(post_response, reverse("inventory:item_detail", args=[item.id]))

    def test_movel_update_view_rejects_other_organizations_item(self):
        other_org = Organization.objects.create(
            name="Outra Org", slug="outra-org",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        other_item = Movel.objects.create(
            organization=other_org, code="PAT-9999", name="Item de outra org",
            category=self.category, sector=self.sector,
        )
        response = self.client.get(reverse("inventory:item_update", args=[other_item.id]))
        self.assertEqual(response.status_code, 404)

    def test_imovel_create_redirects_to_detail(self):
        response = self.client.post(reverse("inventory:imovel_create"), self._imovel_payload())
        imovel = Imovel.objects.get(code="IMV-0001")
        self.assertRedirects(response, reverse("inventory:imovel_detail", args=[imovel.id]))

    def test_imovel_update_view_get_and_post(self):
        imovel = Imovel.objects.create(
            organization=self.organization, code="IMV-0002", name="Filial",
            category=self.imovel_category,
        )

        get_response = self.client.get(reverse("inventory:imovel_update", args=[imovel.id]))
        self.assertEqual(get_response.status_code, 200)

        post_response = self.client.post(
            reverse("inventory:imovel_update", args=[imovel.id]),
            self._imovel_payload(code="IMV-0002", name="Filial Renomeada", cartorio_situacao="registrado"),
        )
        imovel.refresh_from_db()
        self.assertEqual(imovel.name, "Filial Renomeada")
        self.assertEqual(imovel.cartorio_situacao, "registrado")
        self.assertRedirects(post_response, reverse("inventory:imovel_detail", args=[imovel.id]))
