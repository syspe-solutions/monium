from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from apps.inventory.models import Acquisition, Category, Imovel, ImovelCategory, Movel, Sector
from apps.inventory.services.depreciation_service import calculate_depreciation
from apps.organizations.models import (
    Organization,
    OrganizationGoal,
    OrganizationIndustry,
    OrganizationSize,
)


class DepreciationServiceTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Eletrônicos", slug="eletronicos", useful_life_months=60,
        )
        self.category_no_life = Category.objects.create(name="Diversos", slug="diversos")
        self.category_zero_life = Category.objects.create(
            name="Zero Vida Útil", slug="zero-vida-util", useful_life_months=0,
        )
        self.sector = Sector.objects.create(name="TI", slug="ti")
        self.imovel_category = ImovelCategory.objects.create(name="Sede", slug="sede-dep")
        self.organization = Organization.objects.create(
            name="Org Depreciacao", slug="org-depreciacao",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )

    def _movel(self, category, code="PAT-0001"):
        return Movel.objects.create(
            organization=self.organization, code=code, name="Notebook",
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

    def test_returns_non_depreciable_when_category_has_zero_useful_life(self):
        acquisition = Acquisition.objects.create(
            item=self._movel(self.category_zero_life), value=Decimal("1000.00"), purchase_date=date.today(),
        )
        result = calculate_depreciation(acquisition)
        self.assertFalse(result.is_depreciable)
        self.assertEqual(result.current_book_value, Decimal("1000.00"))
        self.assertEqual(result.accumulated_depreciation, Decimal("0"))

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

    def test_future_purchase_date_clamps_elapsed_months_to_zero(self):
        acquisition = Acquisition.objects.create(
            item=self._movel(self.category), value=Decimal("6000.00"),
            purchase_date=date.today() + timedelta(days=30),
        )
        result = calculate_depreciation(acquisition, as_of=date.today())
        self.assertEqual(result.elapsed_months, 0)
        self.assertEqual(result.current_book_value, Decimal("6000.00"))
        self.assertFalse(result.is_fully_depreciated)

    def test_zero_value_acquisition_does_not_raise_division_by_zero(self):
        acquisition = Acquisition.objects.create(
            item=self._movel(self.category), value=Decimal("0.00"),
            purchase_date=date.today() - timedelta(days=30 * 30),
        )
        result = calculate_depreciation(acquisition, as_of=date.today())
        self.assertEqual(result.current_book_value, Decimal("0.00"))
        self.assertEqual(result.depreciation_percent, Decimal("0"))

    def test_item_without_movel_relation_is_not_depreciable(self):
        imovel = Imovel.objects.create(
            organization=self.organization, code="IMV-DEP-0001", name="Sala",
            category=self.imovel_category,
        )
        acquisition = Acquisition.objects.create(
            item=imovel, value=Decimal("150000.00"), purchase_date=date.today(),
        )
        result = calculate_depreciation(acquisition, as_of=date.today())
        self.assertFalse(result.is_depreciable)
        self.assertEqual(result.current_book_value, Decimal("150000.00"))
