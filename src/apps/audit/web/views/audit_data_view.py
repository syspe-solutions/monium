from django.views import View

from django.http import JsonResponse
from apps.security.mixins import PermissionRequiredMixin



class AuditDataView(PermissionRequiredMixin, View):
    required_permission = 'view_business_logs'
    raise_exception = True

    def get(self, request):
        from apps.audit.models import Audit
        try:
            limit = int(request.GET.get('limit', 20))
        except (ValueError, TypeError):
            limit = 20
        
        audits = Audit.objects.all().order_by('-date')[:limit]
        
        data = []
        for audit in audits:
            data.append({
                'date': audit.date.isoformat(),
                'method': audit.method,
                'path': audit.path,
                'response_status_code': audit.response_status_code,
                'total_time': audit.total_time,
                'python_time': audit.python_time,
                'db_time': audit.db_time,
                'total_queries': audit.total_queries,
            })
            
        return JsonResponse(data, safe=False)
