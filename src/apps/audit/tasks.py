import logging

from django.apps import apps

logger = logging.getLogger("audit.tasks")


def record_request_audit(audit_data):
    try:
        Audit = apps.get_model("audit", "Audit")
        Audit.objects.create(**audit_data)
    except Exception as e:
        logger.error(f"Failed to persist Audit: {e}")
