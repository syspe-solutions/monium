import logging

from django.utils import timezone

from apps.inventory.models import Loan, LoanStatus
from apps.inventory.services.loan_notification_service import send_overdue_notice

logger = logging.getLogger("inventory.tasks")


def check_overdue_loans():
    today = timezone.now().date()
    newly_overdue = list(
        Loan.objects.filter(status=LoanStatus.ACTIVE, expected_return__lt=today)
        .select_related("item__organization")
    )

    if not newly_overdue:
        return 0

    Loan.objects.filter(id__in=[loan.id for loan in newly_overdue]).update(status=LoanStatus.OVERDUE)

    for loan in newly_overdue:
        try:
            send_overdue_notice(loan)
        except Exception:
            logger.exception("Falha ao processar alerta de atraso do empréstimo %s", loan.id)

    return len(newly_overdue)
