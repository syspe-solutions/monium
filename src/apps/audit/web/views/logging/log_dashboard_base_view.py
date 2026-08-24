from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from apps.audit.services import LogReaderService
from apps.security.mixins import PermissionRequiredMixin


class BaseLayerDashboardView(PermissionRequiredMixin, View):
    raise_exception = True

    layer = ""
    template_name = ""
    empty_colspan = 4

    def get(self, request):
        if self.layer not in LogReaderService.LAYERS_MAP:
            return HttpResponse("Camada de log invalida", status=404)
        metrics = LogReaderService.get_metrics(self.layer)
        
        return render(
            request,
            self.template_name,
            {
                "segment": f"audit_{self.layer}",
                "current_layer": self.layer,
                "layers": LogReaderService.LAYERS_MAP.keys(),
                "metrics": metrics,
                "empty_colspan": self.empty_colspan,
            },
        )
