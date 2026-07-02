from django.views import View


from django.http import JsonResponse
from apps.audit.services import LogReaderService
from apps.security.mixins import PermissionRequiredMixin


class LogListView(PermissionRequiredMixin, View):
    required_permission = 'view_business_logs'
    raise_exception = True

    def get(self, request):
        try:
            limit = int(request.GET.get('limit', 50))
        except (ValueError, TypeError):
            limit = 50
            
        filters = {
            'level': request.GET.get('level'),
            'q': request.GET.get('q')
        }
        logs = LogReaderService.read_logs('business', limit, filters)
        return JsonResponse(logs, safe=False)
