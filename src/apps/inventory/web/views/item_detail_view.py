from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.inventory.models import Movel


class MovelDetailView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/item_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        organization = self.request.organization

        item = get_object_or_404(
            Movel.objects.select_related("category", "sector", "location").prefetch_related("spec__brand"),
            pk=kwargs["pk"],
            organization=organization,
        )

        ctx["item"] = item
        ctx["loans"] = item.loans.select_related("loaned_by").order_by("-loaned_at")
        return ctx
