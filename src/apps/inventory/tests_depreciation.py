from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.inventory.models import Acquisition, Category, Movel, Sector
from apps.inventory.services.depreciation_service import calculate_depreciation
from apps.inventory.services.portfolio_value_summary import get_portfolio_current_value
from apps.organizations.models import (
    Membership,
    MembershipRole,
    Organization,
    OrganizationGoal,
    OrganizationIndustry,
    OrganizationSize,
)

User = get_user_model()


class DepreciationServiceTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Eletrônicos", slug="eletronicos", useful_life_months=60,
        )
        self.category_no_life = Category.objects.create(name="Diversos", slug="diversos")
        self.sector = Sector.objects.create(name="TI", slug="ti")
        self.organization = Organization.objects.create(
            name="Org Depreciacao", slug="org-depreciacao",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )

    def _movel(self, category):
        return Movel.objects.create(
            organization=self.organization, code="PAT-0001", name="Notebook",
            category=category, sector=self.sector,
        )

    def test_returns_none_without_value_or_purchase_date(self):
        acquisition = Acquisition.objects.create(item=self._movel(self.category))
        self.assertIsNone(calculate_depreciation(acquisition))

    def test_returns_non_depreciable_when_category_has_no_useful_life(self):
        acquisition = Acquisition.objects.create(
            item=self._movel(self.category_no_life), value=Decimal("1000.00"), purchase_date=date.today(),
        )
        result = calculate_depreciation(acquisition)
        self.assertFalse(result.is_depreciable)
        self.assertEqual(result.current_book_value, Decimal("1000.00"))

    def test_linear_depreciation_at_half_of_useful_life(self):
        purchase_date = date.today() - timedelta(days=30 * 30)  # ~30 meses atrás, vida útil de 60
        acquisition = Acquisition.objects.create(
            item=self._movel(self.category), value=Decimal("6000.00"), purchase_date=purchase_date,
        )
        result = calculate_depreciation(acquisition, as_of=date.today())
        self.assertTrue(result.is_depreciable)
        self.assertFalse(result.is_fully_depreciated)
        # ~30 dos 60 meses -> ~metade do valor depreciado
        self.assertAlmostEqual(float(result.current_book_value), 3000.00, delta=110.00)

    def test_fully_depreciated_after_useful_life_caps_at_zero(self):
        purchase_date = date.today() - timedelta(days=30 * 90)  # bem além dos 60 meses de vida útil
        acquisition = Acquisition.objects.create(
            item=self._movel(self.category), value=Decimal("1200.00"), purchase_date=purchase_date,
        )
        result = calculate_depreciation(acquisition, as_of=date.today())
        self.assertTrue(result.is_fully_depreciated)
        self.assertEqual(result.current_book_value, Decimal("0.00"))
        self.assertEqual(result.accumulated_depreciation, Decimal("1200.00"))

    def test_at_purchase_date_book_value_equals_acquisition_value(self):
        acquisition = Acquisition.objects.create(
            item=self._movel(self.category), value=Decimal("6000.00"), purchase_date=date.today(),
        )
        result = calculate_depreciation(acquisition, as_of=date.today())
        self.assertEqual(result.current_book_value, Decimal("6000.00"))
        self.assertEqual(result.elapsed_months, 0)

    def test_explicit_useful_life_months_skips_category_lookup(self):
        acquisition = Acquisition.objects.create(
            item=self._movel(self.category_no_life), value=Decimal("1200.00"),
            purchase_date=date.today() - timedelta(days=30 * 30),
        )
        result = calculate_depreciation(acquisition, as_of=date.today(), useful_life_months=60)
        self.assertTrue(result.is_depreciable)


class PortfolioCurrentValueTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Eletrônicos", slug="eletronicos-2", useful_life_months=60,
        )
        self.sector = Sector.objects.create(name="TI", slug="ti-2")
        self.organization = Organization.objects.create(
            name="Org Carteira", slug="org-carteira",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )

    def test_sums_current_book_value_across_items(self):
        item1 = Movel.objects.create(
            organization=self.organization, code="PAT-0001", name="Notebook",
            category=self.category, sector=self.sector,
        )
        Acquisition.objects.create(item=item1, value=Decimal("6000.00"), purchase_date=date.today())

        item2 = Movel.objects.create(
            organization=self.organization, code="PAT-0002", name="Cadeira",
            category=self.category, sector=self.sector,
        )
        Acquisition.objects.create(item=item2, value=Decimal("500.00"), purchase_date=date.today())

        total = get_portfolio_current_value(self.organization)
        self.assertEqual(total, Decimal("6500.00"))

    def test_ignores_items_without_acquisition_value(self):
        item = Movel.objects.create(
            organization=self.organization, code="PAT-0003", name="Mesa",
            category=self.category, sector=self.sector,
        )
        Acquisition.objects.create(item=item)

        self.assertEqual(get_portfolio_current_value(self.organization), Decimal("0"))


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
