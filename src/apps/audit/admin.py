from django.contrib import admin

from apps.common.admin import BaseModelAdminAbstract

from .models import Audit


@admin.register(Audit)
class AuditorAdmin(BaseModelAdminAbstract):
    list_display = ['date', 'path', 'total_time', 'python_time', 'db_time', 'total_queries']
    list_filter = ['date', 'path', 'method', 'response_status_code']
    search_fields = ['path', 'user_agent', 'ip']
    readonly_fields = ['date', 'path', 'total_time', 'python_time', 'db_time', 'total_queries',
                       'method', 'host', 'port', 'content_type', 'body', 'user_agent',
                       'response_content', 'response_status_code', 'ip', 'proxy_verified']
    ordering = ['-date']
