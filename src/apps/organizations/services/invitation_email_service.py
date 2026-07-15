import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

SUBJECT_TEMPLATE = "organizations/emails/invitation_subject.txt"
BODY_TEMPLATE = "organizations/emails/invitation_body.txt"


def send_invitation_email(invitation, accept_url: str) -> None:
    context = {"invitation": invitation, "organization": invitation.organization, "accept_url": accept_url}
    subject = render_to_string(SUBJECT_TEMPLATE, context).strip()
    body = render_to_string(BODY_TEMPLATE, context)

    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [invitation.email])
    except Exception:
        logger.exception("Falha ao enviar convite para %s (org=%s)", invitation.email, invitation.organization_id)
