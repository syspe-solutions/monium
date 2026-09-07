from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase

from apps.inventory.models import Acquisition, Category, Movel, Sector
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

    def test_returns_zero_when_nothing_is_expiring(self):
        self.acquisition.delete()
        notified = check_expiring_warranties()
        self.assertEqual(notified, 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_a_failure_sending_one_notice_does_not_block_the_others(self):
        item2 = Movel.objects.create(
            organization=self.organization, code="PAT-0002", name="Mouse",
            category=self.category, sector=self.sector,
        )
        Acquisition.objects.create(
            item=item2, value=Decimal("50"), purchase_date=date.today(),
            warranty_expiry=date.today() + timedelta(days=5),
        )

        notified = check_expiring_warranties()

        # Ambas as aquisições são marcadas como processadas mesmo que o envio
        # de uma delas falhe internamente (send_warranty_expiring_notice
        # engole a exceção) — o alerta não deve travar em loop por causa de
        # uma falha isolada de e-mail.
        self.assertEqual(notified, 2)
