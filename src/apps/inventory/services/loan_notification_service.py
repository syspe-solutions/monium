import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

SUBJECT_TEMPLATE = "inventory/emails/loan_overdue_subject.txt"
BODY_TEMPLATE = "inventory/emails/loan_overdue_body.txt"


def send_overdue_notice(loan) -> None:
    recipients = list(
        loan.item.organization.memberships
        .select_related("user")
        .values_list("user__email", flat=True)
    )
    if not recipients:
        return

    context = {"loan": loan, "item": loan.item}
    subject = render_to_string(SUBJECT_TEMPLATE, context).strip()
    body = render_to_string(BODY_TEMPLATE, context)

    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients)
    except Exception:
        logger.exception("Falha ao enviar alerta de atraso para o empréstimo %s", loan.id)
