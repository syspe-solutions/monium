from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import TemplateView

from apps.inventory.models import AssetStatus, Category
from apps.inventory.services.asset_status_summary import get_asset_status_summary


class MovableAssetsByCategoryView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        organization = self.request.organization
        ctx.update(get_asset_status_summary(organization))
        total = ctx["total_items"]

        ctx["categories"] = (
            Category.objects
            .annotate(
                item_count=Count("items", filter=Q(items__organization=organization)),
                active_count=Count("items", filter=Q(items__organization=organization, items__status=AssetStatus.IN_USE)),
                maintenance_count=Count("items", filter=Q(items__organization=organization, items__status=AssetStatus.MAINTENANCE)),
                missing_count=Count("items", filter=Q(items__organization=organization, items__status=AssetStatus.MISSING)),
            )
            .order_by("-item_count")
        )

        ctx["total_for_percent"] = total if total > 0 else 1

        return ctx
