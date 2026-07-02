from django.db import models
from apps.common.models import BaseModelAbstract

class Audit(BaseModelAbstract):
    date = models.DateTimeField(auto_now_add=True)
    
    total_time = models.FloatField()
    python_time = models.FloatField()
    db_time = models.FloatField()
    total_queries = models.IntegerField()

    path = models.TextField()
    method = models.CharField(max_length=10)
    host = models.CharField(max_length=100)
    port = models.IntegerField(null=True)
    content_type = models.CharField(max_length=100, null=True)
    body = models.TextField(null=True)
    user_agent = models.TextField(null=True)
    response_content = models.TextField(null=True)
    response_status_code = models.IntegerField(null=True)

    ip = models.GenericIPAddressField(null=True)
    proxy_verified = models.BooleanField(null=True)

    def __str__(self):
        return f'Auditor: {self.date}'

    class Meta:
        verbose_name = 'Auditor'
        verbose_name_plural = 'Auditor'
