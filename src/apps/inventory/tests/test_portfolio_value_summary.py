from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.inventory.models import Acquisition, Category, MovableAsset, Sector
from apps.inventory.services.portfolio_value_summary import get_portfolio_current_value
from apps.organizations.models import (
    Organization,
    OrganizationGoal,
    OrganizationIndustry,
    OrganizationSize,
)


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
        item1 = MovableAsset.objects.create(
            organization=self.organization, code="PAT-0001", name="Notebook",
            category=self.category, sector=self.sector,
        )
        Acquisition.objects.create(item=item1, value=Decimal("6000.00"), purchase_date=date.today())

        item2 = MovableAsset.objects.create(
            organization=self.organization, code="PAT-0002", name="Cadeira",
            category=self.category, sector=self.sector,
        )
        Acquisition.objects.create(item=item2, value=Decimal("500.00"), purchase_date=date.today())

        total = get_portfolio_current_value(self.organization)
        self.assertEqual(total, Decimal("6500.00"))

    def test_ignores_items_without_acquisition_value(self):
        item = MovableAsset.objects.create(
            organization=self.organization, code="PAT-0003", name="Mesa",
            category=self.category, sector=self.sector,
        )
        Acquisition.objects.create(item=item)

        self.assertEqual(get_portfolio_current_value(self.organization), Decimal("0"))

    def test_returns_zero_for_organization_without_items(self):
        empty_org = Organization.objects.create(
            name="Org Vazia", slug="org-vazia",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        self.assertEqual(get_portfolio_current_value(empty_org), Decimal("0"))
