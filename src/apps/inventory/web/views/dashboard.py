from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import TemplateView

from apps.inventory.models import Category, Item, ItemStatus


class ItemsByCategoryView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        organization = self.request.user.organization
        items = Item.objects.filter(organization=organization)
        total = items.count()

        ctx["total_items"] = total
        ctx["active_items"] = items.filter(status=ItemStatus.ACTIVE).count()
        ctx["maintenance_items"] = items.filter(status=ItemStatus.MAINTENANCE).count()
        ctx["missing_items"] = items.filter(status=ItemStatus.MISSING).count()
        ctx["written_off_items"] = items.filter(status=ItemStatus.WRITTEN_OFF).count()

        ctx["categories"] = (
            Category.objects
            .annotate(
                item_count=Count("items", filter=Q(items__organization=organization)),
                active_count=Count("items", filter=Q(items__organization=organization, items__status=ItemStatus.ACTIVE)),
                maintenance_count=Count("items", filter=Q(items__organization=organization, items__status=ItemStatus.MAINTENANCE)),
                missing_count=Count("items", filter=Q(items__organization=organization, items__status=ItemStatus.MISSING)),
            )
            .order_by("-item_count")
        )

        ctx["total_for_percent"] = total if total > 0 else 1

        return ctx
