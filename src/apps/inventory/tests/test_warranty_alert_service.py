from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from apps.inventory.models import Acquisition, Category, Movel, Sector
from apps.inventory.services.warranty_alert_service import get_expiring_warranties
from apps.organizations.models import (
    Organization,
    OrganizationGoal,
    OrganizationIndustry,
    OrganizationSize,
)


class GetExpiringWarrantiesTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Eletrônicos", slug="eletronicos-ge")
        self.sector = Sector.objects.create(name="TI", slug="ti-ge")
        self.organization = Organization.objects.create(
            name="Org GE", slug="org-ge",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )

    def _acquisition(self, code, warranty_expiry):
        item = Movel.objects.create(
            organization=self.organization, code=code, name=code,
            category=self.category, sector=self.sector,
        )
        return Acquisition.objects.create(
            item=item, value=Decimal("100"), purchase_date=date.today(), warranty_expiry=warranty_expiry,
        )

    def test_includes_warranties_within_window(self):
        acquisition = self._acquisition("PAT-0001", date.today() + timedelta(days=10))
        results = list(get_expiring_warranties(self.organization, within_days=30))
        self.assertEqual(results, [acquisition])

    def test_excludes_already_expired_warranties(self):
        self._acquisition("PAT-0002", date.today() - timedelta(days=1))
        results = list(get_expiring_warranties(self.organization, within_days=30))
        self.assertEqual(results, [])

    def test_excludes_warranties_beyond_the_window(self):
        self._acquisition("PAT-0003", date.today() + timedelta(days=60))
        results = list(get_expiring_warranties(self.organization, within_days=30))
        self.assertEqual(results, [])

    def test_excludes_acquisitions_without_warranty(self):
        item = Movel.objects.create(
            organization=self.organization, code="PAT-0004", name="Sem garantia",
            category=self.category, sector=self.sector,
        )
        Acquisition.objects.create(item=item, value=Decimal("100"), purchase_date=date.today())
        results = list(get_expiring_warranties(self.organization, within_days=30))
        self.assertEqual(results, [])

    def test_warranty_expiring_today_is_included(self):
        acquisition = self._acquisition("PAT-0005", date.today())
        results = list(get_expiring_warranties(self.organization, within_days=30))
        self.assertEqual(results, [acquisition])

    def test_organization_filter_excludes_other_organizations_warranties(self):
        self._acquisition("PAT-0006", date.today() + timedelta(days=5))
        other_org = Organization.objects.create(
            name="Outra Org GE", slug="outra-org-ge",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        results = list(get_expiring_warranties(other_org, within_days=30))
        self.assertEqual(results, [])

    def test_without_organization_filter_returns_warranties_across_all_organizations(self):
        acquisition = self._acquisition("PAT-0007", date.today() + timedelta(days=5))
        results = list(get_expiring_warranties(within_days=30))
        self.assertIn(acquisition, results)
