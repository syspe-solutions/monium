from django.http import HttpResponse
from django.views import View

from apps.audit.services import LogReaderService
from apps.security.mixins import PermissionRequiredMixin
from apps.audit.web.views.logging.access_log_dashboard_view import AccessLogDashboardView
from apps.audit.web.views.logging.business_log_dashboard_view import BusinessLogDashboardView
from apps.audit.web.views.logging.celery_log_dashboard_view import CeleryLogDashboardView
from apps.audit.web.views.logging.database_log_dashboard_view import DatabaseLogDashboardView
from apps.audit.web.views.logging.error_log_dashboard_view import ErrorLogDashboardView
from apps.audit.web.views.logging.performance_log_dashboard_view import PerformanceLogDashboardView
from apps.audit.web.views.logging.security_log_dashboard_view import SecurityLogDashboardView


class LogLayerDashboardView(PermissionRequiredMixin, View):
    raise_exception = True

    VIEW_MAP = {
        "business": BusinessLogDashboardView,
        "access": AccessLogDashboardView,
        "security": SecurityLogDashboardView,
        "performance": PerformanceLogDashboardView,
        "error": ErrorLogDashboardView,
        "celery": CeleryLogDashboardView,
        "database": DatabaseLogDashboardView,
    }

    def get(self, request, layer):
        if layer not in LogReaderService.LAYERS_MAP:
            return HttpResponse("Camada de log inválida", status=404)

        view_class = self.VIEW_MAP[layer]
        return view_class.as_view()(request)

