from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.inventory.models import (
    Acquisition,
    Category,
    Loan,
    LoanStatus,
    MovableAsset,
    RealEstateAsset,
    RealEstateCategory,
    Sector,
)
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
        self.real_estate_category = RealEstateCategory.objects.create(name="Sede", slug="sede")
        self.client.force_login(self.user)

    def _movable_asset_payload(self, **overrides):
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

    def _real_estate_payload(self, **overrides):
        payload = {
            "code": "IMV-0001",
            "name": "Sede Central",
            "category": self.real_estate_category.id,
            "ownership": "proprio",
            "condition": "bom",
            "cartorio_situacao": "nao_registrado",
        }
        payload.update(overrides)
        return payload

    def test_movable_asset_create_redirects_to_detail(self):
        response = self.client.post(reverse("inventory:item_create"), self._movable_asset_payload())
        item = MovableAsset.objects.get(code="PAT-0001")
        self.assertRedirects(response, reverse("inventory:item_detail", args=[item.id]))

    def test_movable_asset_update_view_get_and_post(self):
        item = MovableAsset.objects.create(
            organization=self.organization, code="PAT-0002", name="Mouse",
            category=self.category, sector=self.sector, status="em_uso",
        )

        get_response = self.client.get(reverse("inventory:item_update", args=[item.id]))
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, "Mouse")

        post_response = self.client.post(
            reverse("inventory:item_update", args=[item.id]),
            self._movable_asset_payload(code="PAT-0002", name="Mouse sem fio", status="em_manutencao"),
        )
        item.refresh_from_db()
        self.assertEqual(item.name, "Mouse sem fio")
        self.assertEqual(item.status, "em_manutencao")
        self.assertRedirects(post_response, reverse("inventory:item_detail", args=[item.id]))

    def test_movable_asset_create_saves_acquisition_value(self):
        self.client.post(reverse("inventory:item_create"), self._movable_asset_payload(
            value="4500.00", purchase_date="2026-01-15",
        ))
        item = MovableAsset.objects.get(code="PAT-0001")
        self.assertEqual(item.acquisition.value, Decimal("4500.00"))
        self.assertEqual(item.acquisition.purchase_date, date(2026, 1, 15))

    def test_movable_asset_create_without_acquisition_data_creates_no_acquisition(self):
        self.client.post(reverse("inventory:item_create"), self._movable_asset_payload())
        item = MovableAsset.objects.get(code="PAT-0001")
        self.assertFalse(Acquisition.objects.filter(item=item).exists())

    def test_movable_asset_update_sets_acquisition_value(self):
        item = MovableAsset.objects.create(
            organization=self.organization, code="PAT-0003", name="Impressora",
            category=self.category, sector=self.sector, status="em_uso",
        )
        self.client.post(
            reverse("inventory:item_update", args=[item.id]),
            self._movable_asset_payload(code="PAT-0003", name="Impressora", value="899.90", purchase_date="2026-02-01"),
        )
        item.refresh_from_db()
        self.assertEqual(item.acquisition.value, Decimal("899.90"))

    def test_movable_asset_update_edits_existing_acquisition_value(self):
        item = MovableAsset.objects.create(
            organization=self.organization, code="PAT-0004", name="Cadeira",
            category=self.category, sector=self.sector, status="em_uso",
        )
        Acquisition.objects.create(item=item, value=Decimal("100.00"), purchase_date=date(2025, 1, 1))

        self.client.post(
            reverse("inventory:item_update", args=[item.id]),
            self._movable_asset_payload(code="PAT-0004", name="Cadeira", value="150.00", purchase_date="2025-06-01"),
        )
        item.refresh_from_db()
        self.assertEqual(item.acquisition.value, Decimal("150.00"))
        self.assertEqual(Acquisition.objects.filter(item=item).count(), 1)

    def test_movable_asset_delete_confirm_page_loads(self):
        item = MovableAsset.objects.create(
            organization=self.organization, code="PAT-0005", name="Teclado",
            category=self.category, sector=self.sector, status="em_uso",
        )
        response = self.client.get(reverse("inventory:item_delete", args=[item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PAT-0005")

    def test_movable_asset_delete_requires_matching_code_confirmation(self):
        item = MovableAsset.objects.create(
            organization=self.organization, code="PAT-0006", name="Mesa",
            category=self.category, sector=self.sector, status="em_uso",
        )
        response = self.client.post(
            reverse("inventory:item_delete", args=[item.id]),
            {"confirmation_code": "WRONG-CODE"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(MovableAsset.objects.filter(pk=item.id).exists())

    def test_movable_asset_delete_succeeds_with_matching_code(self):
        item = MovableAsset.objects.create(
            organization=self.organization, code="PAT-0007", name="Monitor",
            category=self.category, sector=self.sector, status="em_uso",
        )
        Acquisition.objects.create(item=item, value=Decimal("300.00"), purchase_date=date.today())

        response = self.client.post(
            reverse("inventory:item_delete", args=[item.id]),
            {"confirmation_code": "PAT-0007"},
        )
        self.assertRedirects(response, reverse("inventory:item_list"))
        self.assertFalse(MovableAsset.objects.filter(pk=item.id).exists())
        self.assertFalse(Acquisition.objects.filter(item_id=item.id).exists())

    def test_movable_asset_delete_is_blocked_when_item_has_loan_history(self):
        item = MovableAsset.objects.create(
            organization=self.organization, code="PAT-0008", name="Notebook Emprestado",
            category=self.category, sector=self.sector, status="em_uso",
        )
        Loan.objects.create(
            item=item, loaned_to="Fulano", loaned_at=timezone.now(),
            expected_return=date.today(), status=LoanStatus.RETURNED,
        )

        response = self.client.post(
            reverse("inventory:item_delete", args=[item.id]),
            {"confirmation_code": "PAT-0008"},
        )
        self.assertRedirects(response, reverse("inventory:item_detail", args=[item.id]))
        self.assertTrue(MovableAsset.objects.filter(pk=item.id).exists())

    def test_movable_asset_update_view_rejects_other_organizations_item(self):
        other_org = Organization.objects.create(
            name="Outra Org", slug="outra-org",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        other_item = MovableAsset.objects.create(
            organization=other_org, code="PAT-9999", name="Item de outra org",
            category=self.category, sector=self.sector,
        )
        response = self.client.get(reverse("inventory:item_update", args=[other_item.id]))
        self.assertEqual(response.status_code, 404)

    def test_real_estate_create_redirects_to_detail(self):
        response = self.client.post(reverse("inventory:real_estate_create"), self._real_estate_payload())
        real_estate = RealEstateAsset.objects.get(code="IMV-0001")
        self.assertRedirects(response, reverse("inventory:real_estate_detail", args=[real_estate.id]))

    def test_real_estate_update_view_get_and_post(self):
        real_estate = RealEstateAsset.objects.create(
            organization=self.organization, code="IMV-0002", name="Filial",
            category=self.real_estate_category,
        )

        get_response = self.client.get(reverse("inventory:real_estate_update", args=[real_estate.id]))
        self.assertEqual(get_response.status_code, 200)

        post_response = self.client.post(
            reverse("inventory:real_estate_update", args=[real_estate.id]),
            self._real_estate_payload(code="IMV-0002", name="Filial Renomeada", cartorio_situacao="registrado"),
        )
        real_estate.refresh_from_db()
        self.assertEqual(real_estate.name, "Filial Renomeada")
        self.assertEqual(real_estate.cartorio_situacao, "registrado")
        self.assertRedirects(post_response, reverse("inventory:real_estate_detail", args=[real_estate.id]))
