from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.inventory.models import Imovel


class ImovelDetailView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/imovel_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        organization = self.request.organization

        imovel = get_object_or_404(
            Imovel.objects.select_related("category"),
            pk=kwargs["pk"],
            organization=organization,
        )

        ctx["imovel"] = imovel
        return ctx
