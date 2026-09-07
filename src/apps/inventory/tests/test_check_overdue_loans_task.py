from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from apps.inventory.models import Category, Loan, LoanStatus, Movel, Sector
from apps.inventory.tasks import check_overdue_loans
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


class CheckOverdueLoansTaskTests(TestCase):
    """`check_overdue_loans` não tinha nenhum teste direto — só era exercitada
    indiretamente. Cobre a transição de status ACTIVE -> OVERDUE e o disparo
    (idempotente) do e-mail de alerta."""

    def setUp(self):
        configure_email_settings()
        self.category = Category.objects.create(name="Eletrônicos", slug="eletronicos-loan")
        self.sector = Sector.objects.create(name="TI", slug="ti-loan")
        self.organization = Organization.objects.create(
            name="Org Loan", slug="org-loan",
            industry=OrganizationIndustry.values[0], size=OrganizationSize.values[0],
            primary_goal=OrganizationGoal.values[0],
        )
        self.user = User.objects.create_user(
            username="loanuser", email="loanuser@example.com", password="12345",
        )
        Membership.objects.create(organization=self.organization, user=self.user, role=MembershipRole.OWNER)
        self.item = Movel.objects.create(
            organization=self.organization, code="PAT-0001", name="Notebook",
            category=self.category, sector=self.sector,
        )

    def _loan(self, expected_return, status=LoanStatus.ACTIVE, code_suffix=""):
        return Loan.objects.create(
            item=self.item, loaned_to=f"Fulano{code_suffix}", loaned_at=timezone.now(),
            expected_return=expected_return, status=status,
        )

    def test_marks_active_loan_past_due_date_as_overdue(self):
        loan = self._loan(expected_return=date.today() - timedelta(days=1))

        newly_overdue = check_overdue_loans()

        self.assertEqual(newly_overdue, 1)
        loan.refresh_from_db()
        self.assertEqual(loan.status, LoanStatus.OVERDUE)

    def test_sends_overdue_notice_email(self):
        self._loan(expected_return=date.today() - timedelta(days=1))

        check_overdue_loans()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("loanuser@example.com", mail.outbox[0].to)

    def test_does_not_touch_active_loans_not_yet_due(self):
        loan = self._loan(expected_return=date.today() + timedelta(days=5))

        newly_overdue = check_overdue_loans()

        self.assertEqual(newly_overdue, 0)
        loan.refresh_from_db()
        self.assertEqual(loan.status, LoanStatus.ACTIVE)
        self.assertEqual(len(mail.outbox), 0)

    def test_loan_due_today_is_not_yet_overdue(self):
        loan = self._loan(expected_return=date.today())

        newly_overdue = check_overdue_loans()

        self.assertEqual(newly_overdue, 0)
        loan.refresh_from_db()
        self.assertEqual(loan.status, LoanStatus.ACTIVE)

    def test_does_not_resend_notice_for_a_loan_already_marked_overdue(self):
        self._loan(expected_return=date.today() - timedelta(days=1), status=LoanStatus.OVERDUE)

        newly_overdue = check_overdue_loans()

        self.assertEqual(newly_overdue, 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_ignores_returned_loans_even_if_past_expected_return(self):
        loan = self._loan(expected_return=date.today() - timedelta(days=10), status=LoanStatus.RETURNED)

        newly_overdue = check_overdue_loans()

        self.assertEqual(newly_overdue, 0)
        loan.refresh_from_db()
        self.assertEqual(loan.status, LoanStatus.RETURNED)

    def test_processes_multiple_overdue_loans_in_one_run(self):
        self._loan(expected_return=date.today() - timedelta(days=1), code_suffix="A")
        self._loan(expected_return=date.today() - timedelta(days=3), code_suffix="B")

        newly_overdue = check_overdue_loans()

        self.assertEqual(newly_overdue, 2)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(Loan.objects.filter(status=LoanStatus.OVERDUE).count(), 2)

    def test_returns_zero_when_there_is_nothing_overdue(self):
        self.assertEqual(check_overdue_loans(), 0)
        self.assertEqual(len(mail.outbox), 0)
