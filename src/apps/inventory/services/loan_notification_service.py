import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string

from apps.settings.services.email_configuration_resolver_service import (
    EmailConfigurationResolverService,
)

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
        from_email = EmailConfigurationResolverService().resolve().default_from_email
        send_mail(subject, body, from_email, recipients)
    except Exception:
        logger.exception("Falha ao enviar alerta de atraso para o empréstimo %s", loan.id)
