import os
from datetime import datetime

from django.http import HttpResponse
from django.views import View

from apps.audit.services import LogReaderService
from apps.security.mixins import PermissionRequiredMixin


class LogExportView(PermissionRequiredMixin, View):
    raise_exception = True

    def get(self, request, layer):
        path = LogReaderService.get_file_path(layer)
        if not os.path.exists(path):
            return HttpResponse("Arquivo de log não encontrado no servidor.", status=404)

        try:
            with open(path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='text/plain')
                filename = f"{layer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
        except Exception as e:
            return HttpResponse(f"Erro ao exportar log: {str(e)}", status=500)