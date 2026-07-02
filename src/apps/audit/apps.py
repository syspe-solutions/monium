from django.apps import AppConfig
import logging
import os 

logger = logging.getLogger("audit.config")

class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audit'

    def ready(self):
       pass