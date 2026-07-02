from celery import shared_task
from django.apps import apps
import logging

logger = logging.getLogger("audit.tasks")

@shared_task
def record_request_audit(audit_data):
    try:
        Audit = apps.get_model("audit", "Audit")
        Audit.objects.create(**audit_data)
    except Exception as e:
        logger.error(f"Failed to persist Audit async: {e}")
