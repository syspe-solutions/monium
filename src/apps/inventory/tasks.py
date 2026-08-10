import logging

from django.utils import timezone

from apps.inventory.models import Acquisition, Loan, LoanStatus
from apps.inventory.services.loan_notification_service import send_overdue_notice
from apps.inventory.services.warranty_alert_service import (
    DEFAULT_WARNING_WINDOW_DAYS,
    get_expiring_warranties,
)
from apps.inventory.services.warranty_notification_service import send_warranty_expiring_notice

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


def check_expiring_warranties(within_days: int = DEFAULT_WARNING_WINDOW_DAYS):
    """`warranty_alert_sent_at` garante que cada garantia só gera um e-mail —
    sem isso, a mesma aquisição seria notificada todo dia enquanto estivesse
    dentro da janela de aviso (mesmo problema que check_overdue_loans evita
    naturalmente via a transição de status ACTIVE -> OVERDUE)."""
    expiring = list(
        get_expiring_warranties(within_days=within_days)
        .filter(warranty_alert_sent_at__isnull=True)
        .select_related("item__organization")
    )

    if not expiring:
        return 0

    Acquisition.objects.filter(id__in=[a.id for a in expiring]).update(warranty_alert_sent_at=timezone.now())

    for acquisition in expiring:
        try:
            send_warranty_expiring_notice(acquisition)
        except Exception:
            logger.exception("Falha ao processar alerta de garantia da aquisição %s", acquisition.id)

    return len(expiring)
