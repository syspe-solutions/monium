from django.http import HttpResponse
from django.views import View

from apps.audit.services import LogReaderService
from apps.security.mixins import PermissionRequiredMixin
from apps.audit.web.views.logging.log_dashboard_views import (
    AccessLogDashboardView,
    BusinessLogDashboardView,
    CeleryLogDashboardView,
    DatabaseLogDashboardView,
    ErrorLogDashboardView,
    PerformanceLogDashboardView,
    SecurityLogDashboardView,
)


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

