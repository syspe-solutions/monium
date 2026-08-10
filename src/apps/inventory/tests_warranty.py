from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from apps.inventory.forms.acquisition_form import AcquisitionForm
from apps.inventory.models import Acquisition, Category, Movel, Sector
from apps.inventory.services.warranty_alert_service import get_expiring_warranties
from apps.inventory.tasks import check_expiring_warranties
from apps.organizations.models import (
    Membership,
    MembershipRole,
    Organization,
    OrganizationGoal,
    OrganizationIndustry,
    OrganizationSize,
)
from apps.settings.models import EmailSettings

User = get_user_model()


def configure_email_settings():
    email_settings = EmailSettings.load()
    email_settings.is_enabled = True
    email_settings.host = "smtp.example.com"
    email_settings.default_from_email = "no-reply@example.com"
    email_settings.save()


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
        from django.utils import timezone
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


class CheckExpiringWarrantiesTaskTests(TestCase):
    def setUp(self):
        configure_email_settings()
        self.category = Category.objects.create(name="Eletrônicos", slug="eletronicos-task")
        self.sector = Sector.objects.create(name="TI", slug="ti-task")
        self.organization = Organization.objects.create(
            name="Org Task", slug="org-task",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        self.user = User.objects.create_user(
            username="taskuser", email="taskuser@example.com", password="12345",
        )
        Membership.objects.create(organization=self.organization, user=self.user, role=MembershipRole.OWNER)

        item = Movel.objects.create(
            organization=self.organization, code="PAT-0001", name="Notebook",
            category=self.category, sector=self.sector,
        )
        self.acquisition = Acquisition.objects.create(
            item=item, value=Decimal("1000"), purchase_date=date.today(),
            warranty_expiry=date.today() + timedelta(days=10),
        )

    def test_sends_notice_and_marks_as_sent(self):
        notified = check_expiring_warranties()

        self.assertEqual(notified, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("taskuser@example.com", mail.outbox[0].to)

        self.acquisition.refresh_from_db()
        self.assertIsNotNone(self.acquisition.warranty_alert_sent_at)

    def test_does_not_resend_once_already_notified(self):
        check_expiring_warranties()
        mail.outbox.clear()

        notified_again = check_expiring_warranties()

        self.assertEqual(notified_again, 0)
        self.assertEqual(len(mail.outbox), 0)
