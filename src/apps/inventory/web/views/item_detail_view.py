from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView

from apps.inventory.models import MovableAsset
from apps.inventory.services.depreciation_service import calculate_depreciation

WARRANTY_EXPIRING_SOON_DAYS = 30


class MovableAssetDetailView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/item_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        organization = self.request.organization

        item = get_object_or_404(
            MovableAsset.objects.select_related("category", "sector", "location", "acquisition").prefetch_related("spec__brand"),
            pk=kwargs["pk"],
            organization=organization,
        )

        ctx["item"] = item
        ctx["loans"] = item.loans.select_related("loaned_by").order_by("-loaned_at")

        acquisition = getattr(item, "acquisition", None)
        ctx["acquisition"] = acquisition
        ctx["depreciation"] = (
            calculate_depreciation(acquisition, useful_life_months=item.category.useful_life_months)
            if acquisition
            else None
        )
        ctx["warranty_status"] = self._warranty_status(acquisition)
        return ctx

    def _warranty_status(self, acquisition):
        if not acquisition or not acquisition.warranty_expiry:
            return None
        days_left = (acquisition.warranty_expiry - timezone.now().date()).days
        if days_left < 0:
            return "expired"
        if days_left <= WARRANTY_EXPIRING_SOON_DAYS:
            return "expiring_soon"
        return "ok"
