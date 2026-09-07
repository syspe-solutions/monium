from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.inventory.models import RealEstateAsset


class RealEstateDetailView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/real_estate_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        organization = self.request.organization

        real_estate = get_object_or_404(
            RealEstateAsset.objects.select_related("category"),
            pk=kwargs["pk"],
            organization=organization,
        )

        ctx["real_estate"] = real_estate
        return ctx
