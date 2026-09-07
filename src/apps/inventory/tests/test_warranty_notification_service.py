from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase

from apps.inventory.models import Acquisition, Category, MovableAsset, Sector
from apps.inventory.services.warranty_notification_service import send_warranty_expiring_notice
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


class SendWarrantyExpiringNoticeTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Eletrônicos", slug="eletronicos-swen")
        self.sector = Sector.objects.create(name="TI", slug="ti-swen")
        self.organization = Organization.objects.create(
            name="Org SWEN", slug="org-swen",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        self.item = MovableAsset.objects.create(
            organization=self.organization, code="PAT-0001", name="Notebook",
            category=self.category, sector=self.sector,
        )
        self.acquisition = Acquisition.objects.create(
            item=self.item, value=Decimal("1000"), purchase_date=date.today(),
            warranty_expiry=date.today() + timedelta(days=10),
        )

    def test_sends_email_to_every_organization_member(self):
        configure_email_settings()
        user_a = User.objects.create_user(username="member-a", email="a@example.com", password="12345")
        user_b = User.objects.create_user(username="member-b", email="b@example.com", password="12345")
        Membership.objects.create(organization=self.organization, user=user_a, role=MembershipRole.OWNER)
        Membership.objects.create(organization=self.organization, user=user_b, role=MembershipRole.OPERATOR)

        send_warranty_expiring_notice(self.acquisition)

        self.assertEqual(len(mail.outbox), 1)
        self.assertCountEqual(mail.outbox[0].to, ["a@example.com", "b@example.com"])

    def test_does_not_send_when_organization_has_no_members(self):
        configure_email_settings()

        send_warranty_expiring_notice(self.acquisition)

        self.assertEqual(len(mail.outbox), 0)

    def test_swallows_exceptions_instead_of_propagating(self):
        user = User.objects.create_user(username="member-c", email="c@example.com", password="12345")
        Membership.objects.create(organization=self.organization, user=user, role=MembershipRole.OWNER)

        send_warranty_expiring_notice(self.acquisition)  # não deve levantar exceção
