from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import TemplateView

from apps.inventory.models import Category, Item, ItemStatus


class ItemsByCategoryView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        total = Item.objects.count()

        ctx["total_items"] = total
        ctx["active_items"] = Item.objects.filter(status=ItemStatus.ACTIVE).count()
        ctx["maintenance_items"] = Item.objects.filter(status=ItemStatus.MAINTENANCE).count()
        ctx["missing_items"] = Item.objects.filter(status=ItemStatus.MISSING).count()
        ctx["written_off_items"] = Item.objects.filter(status=ItemStatus.WRITTEN_OFF).count()

        ctx["categories"] = (
            Category.objects
            .annotate(
                item_count=Count("items"),
                active_count=Count("items", filter=Q(items__status=ItemStatus.ACTIVE)),
                maintenance_count=Count("items", filter=Q(items__status=ItemStatus.MAINTENANCE)),
                missing_count=Count("items", filter=Q(items__status=ItemStatus.MISSING)),
            )
            .order_by("-item_count")
        )

        ctx["total_for_percent"] = total if total > 0 else 1

        return ctx
