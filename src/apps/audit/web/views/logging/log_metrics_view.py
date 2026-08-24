from django.views import View
from django.http import JsonResponse
from apps.audit.services import LogReaderService
from apps.security.mixins import PermissionRequiredMixin


class LogMetricsView(PermissionRequiredMixin, View):
    raise_exception = True

    def get(self, request, layer):
        metrics = LogReaderService.get_metrics(layer)
        return JsonResponse(metrics)
