from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic import TemplateView

from apps.inventory.models import (
    Category,
    Item,
    ItemCondition,
    ItemStatus,
    Loan,
    LoanStatus,
    Maintenance,
    MaintenanceStatus,
    Sector,
)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()
        seven_days_ago = today - timedelta(days=7)

        # ── Resumo de status ─────────────────────────────────────────────────
        total = Item.objects.count()
        ctx["total_items"] = total
        ctx["active_items"] = Item.objects.filter(status=ItemStatus.ACTIVE).count()
        ctx["maintenance_items"] = Item.objects.filter(status=ItemStatus.MAINTENANCE).count()
        ctx["missing_items"] = Item.objects.filter(status=ItemStatus.MISSING).count()
        ctx["written_off_items"] = Item.objects.filter(status=ItemStatus.WRITTEN_OFF).count()

        # ── Alertas ───────────────────────────────────────────────────────────
        ctx["overdue_loans"] = Loan.objects.filter(
            status=LoanStatus.OVERDUE
        ).select_related("item")[:5]

        ctx["overdue_loans_count"] = Loan.objects.filter(
            status=LoanStatus.OVERDUE
        ).count()

        # Empréstimos ativos com prazo vencido (não marcados como atrasado ainda)
        ctx["loans_past_due"] = Loan.objects.filter(
            status=LoanStatus.ACTIVE,
            expected_return__lt=today,
        ).select_related("item").count()

        ctx["open_maintenances"] = Maintenance.objects.filter(
            status__in=[MaintenanceStatus.OPEN, MaintenanceStatus.IN_PROGRESS],
            started_at__lte=seven_days_ago,
        ).select_related("item")[:5]

        ctx["open_maintenances_count"] = Maintenance.objects.filter(
            status__in=[MaintenanceStatus.OPEN, MaintenanceStatus.IN_PROGRESS],
            started_at__lte=seven_days_ago,
        ).count()

        ctx["poor_condition_active"] = Item.objects.filter(
            condition=ItemCondition.POOR,
            status=ItemStatus.ACTIVE,
        ).count()

        # ── Atividade recente ────────────────────────────────────────────────
        ctx["recent_items"] = (
            Item.objects
            .select_related("category", "sector")
            .order_by("-created_at")[:8]
        )

        # ── Distribuição por categoria ────────────────────────────────────────
        ctx["categories_dist"] = (
            Category.objects
            .annotate(item_count=Count("items"))
            .filter(item_count__gt=0)
            .order_by("-item_count")[:6]
        )
        ctx["categories_total"] = total if total > 0 else 1

        # ── Top setores ───────────────────────────────────────────────────────
        ctx["sectors_dist"] = (
            Sector.objects
            .annotate(item_count=Count("items"))
            .filter(item_count__gt=0)
            .order_by("-item_count")[:5]
        )

        return ctx
