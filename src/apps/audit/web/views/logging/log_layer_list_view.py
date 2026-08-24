from django.http import JsonResponse
from django.views import View

from apps.audit.services import LogReaderService
from apps.security.mixins import PermissionRequiredMixin


class LogLayerListView(PermissionRequiredMixin, View):
    raise_exception = True

    def get(self, request, layer):
        try:
            limit = int(request.GET.get('limit', 50))
        except (ValueError, TypeError):
            limit = 50
            
        filters = {
            'level': request.GET.get('level'),
            'q': request.GET.get('q'),
            'trace_id': request.GET.get('trace_id'),
        }
        
        logs = LogReaderService.read_logs(layer, limit, filters)
        return JsonResponse(logs, safe=False)
