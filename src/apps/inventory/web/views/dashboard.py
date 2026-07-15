from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import TemplateView

from apps.inventory.models import Category, Movel, MovelStatus


class MovelsByCategoryView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        organization = self.request.organization
        items = Movel.objects.filter(organization=organization)
        total = items.count()

        ctx["total_items"] = total
        ctx["active_items"] = items.filter(status=MovelStatus.IN_USE).count()
        ctx["maintenance_items"] = items.filter(status=MovelStatus.MAINTENANCE).count()
        ctx["missing_items"] = items.filter(status=MovelStatus.MISSING).count()
        ctx["written_off_items"] = items.filter(status=MovelStatus.DISCARDED).count()

        ctx["categories"] = (
            Category.objects
            .annotate(
                item_count=Count("items", filter=Q(items__organization=organization)),
                active_count=Count("items", filter=Q(items__organization=organization, items__status=MovelStatus.IN_USE)),
                maintenance_count=Count("items", filter=Q(items__organization=organization, items__status=MovelStatus.MAINTENANCE)),
                missing_count=Count("items", filter=Q(items__organization=organization, items__status=MovelStatus.MISSING)),
            )
            .order_by("-item_count")
        )

        ctx["total_for_percent"] = total if total > 0 else 1

        return ctx
