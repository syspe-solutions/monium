from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.inventory.forms.acquisition_form import AcquisitionForm
from apps.inventory.models import Acquisition, Category, Movel, Sector
from apps.organizations.models import (
    Organization,
    OrganizationGoal,
    OrganizationIndustry,
    OrganizationSize,
)


class AcquisitionFormWarrantyTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Eletrônicos", slug="eletronicos-w")
        self.sector = Sector.objects.create(name="TI", slug="ti-w")
        self.organization = Organization.objects.create(
            name="Org Form", slug="org-form",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        self.item = Movel.objects.create(
            organization=self.organization, code="PAT-0001", name="Notebook",
            category=self.category, sector=self.sector,
        )

    def test_warranty_expiry_is_derived_from_purchase_date_and_months(self):
        form = AcquisitionForm(data={
            "value": "1000.00", "purchase_date": "2026-01-15", "warranty_months": "12",
        })
        self.assertTrue(form.is_valid(), form.errors)
        acquisition = form.save(commit=False)
        acquisition.item = self.item
        acquisition.save()

        self.assertEqual(acquisition.warranty_expiry, date(2027, 1, 15))

    def test_without_warranty_months_expiry_stays_empty(self):
        form = AcquisitionForm(data={"value": "1000.00", "purchase_date": "2026-01-15"})
        self.assertTrue(form.is_valid(), form.errors)
        acquisition = form.save(commit=False)
        acquisition.item = self.item
        acquisition.save()

        self.assertIsNone(acquisition.warranty_expiry)

    def test_changing_warranty_resets_the_alert_flag(self):
        acquisition = Acquisition.objects.create(
            item=self.item, value=Decimal("1000.00"), purchase_date=date(2026, 1, 15),
            warranty_months=12, warranty_expiry=date(2027, 1, 15),
        )
        acquisition.warranty_alert_sent_at = timezone.now()
        acquisition.save()

        form = AcquisitionForm(
            data={"value": "1000.00", "purchase_date": "2026-01-15", "warranty_months": "24"},
            instance=acquisition,
        )
        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()

        self.assertEqual(updated.warranty_expiry, date(2028, 1, 15))
        self.assertIsNone(updated.warranty_alert_sent_at)

    def test_removing_warranty_months_clears_expiry(self):
        acquisition = Acquisition.objects.create(
            item=self.item, value=Decimal("1000.00"), purchase_date=date(2026, 1, 15),
            warranty_months=12, warranty_expiry=date(2027, 1, 15), warranty_alert_sent_at=timezone.now(),
        )

        form = AcquisitionForm(
            data={"value": "1000.00", "purchase_date": "2026-01-15"}, instance=acquisition,
        )
        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()

        self.assertIsNone(updated.warranty_expiry)
