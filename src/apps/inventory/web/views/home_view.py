from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic import TemplateView

from apps.inventory.models import (
    Category,
    RealEstateAsset,
    ItemCondition,
    Loan,
    LoanStatus,
    Maintenance,
    MaintenanceStatus,
    MovableAsset,
    AssetStatus,
    Sector,
)
from apps.inventory.services.asset_status_summary import get_asset_status_summary
from apps.inventory.services.portfolio_value_summary import (
    get_portfolio_current_value,
    get_portfolio_total_value,
    get_top_valued_items,
    get_value_by_month,
)
from apps.inventory.services.warranty_alert_service import get_expiring_warranties


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()
        seven_days_ago = today - timedelta(days=7)
        organization = self.request.organization

        # ── Resumo de status (bens móveis) ──────────────────────────────────
        items = MovableAsset.objects.filter(organization=organization)
        total = items.count()
        ctx.update(get_asset_status_summary(organization))

        # ── Resumo de imóveis ─────────────────────────────────────────────────
        ctx["total_imoveis"] = RealEstateAsset.objects.filter(organization=organization).count()

        # ── Alertas ───────────────────────────────────────────────────────────
        org_loans = Loan.objects.filter(item__organization=organization)

        ctx["overdue_loans"] = org_loans.filter(
            status=LoanStatus.OVERDUE
        ).select_related("item")[:5]

        ctx["overdue_loans_count"] = org_loans.filter(
            status=LoanStatus.OVERDUE
        ).count()

        # Empréstimos ativos com prazo vencido (check_overdue_loans transiciona pra "atrasado" periodicamente)
        ctx["loans_past_due"] = org_loans.filter(
            status=LoanStatus.ACTIVE,
            expected_return__lt=today,
        ).select_related("item").count()

        ctx["open_maintenances"] = Maintenance.objects.filter(
            item__organization=organization,
            status__in=[MaintenanceStatus.OPEN, MaintenanceStatus.IN_PROGRESS],
            started_at__lte=seven_days_ago,
        ).select_related("item")[:5]

        ctx["open_maintenances_count"] = Maintenance.objects.filter(
            item__organization=organization,
            status__in=[MaintenanceStatus.OPEN, MaintenanceStatus.IN_PROGRESS],
            started_at__lte=seven_days_ago,
        ).count()

        ctx["poor_condition_active"] = items.filter(
            condition=ItemCondition.POOR,
            status=AssetStatus.IN_USE,
        ).count()

        expiring_warranties = get_expiring_warranties(organization)
        ctx["expiring_warranties"] = expiring_warranties[:5]
        ctx["expiring_warranties_count"] = expiring_warranties.count()

        # ── Atividade recente ────────────────────────────────────────────────
        ctx["recent_items"] = (
            items
            .select_related("category", "sector")
            .order_by("-created_at")[:8]
        )

        # ── Distribuição por categoria ────────────────────────────────────────
        ctx["categories_dist"] = (
            Category.objects
            .annotate(item_count=Count("items", filter=Q(items__organization=organization)))
            .filter(item_count__gt=0)
            .order_by("-item_count")[:6]
        )
        ctx["categories_total"] = total if total > 0 else 1

        # ── Top setores ───────────────────────────────────────────────────────
        ctx["sectors_dist"] = (
            Sector.objects
            .annotate(item_count=Count("items", filter=Q(items__organization=organization)))
            .filter(item_count__gt=0)
            .order_by("-item_count")[:5]
        )

        # ── Carteira (valor do acervo) ───────────────────────────────────────
        ctx["portfolio_total_value"] = get_portfolio_total_value(organization)
        ctx["portfolio_current_value"] = get_portfolio_current_value(organization)
        ctx["top_valued_items"] = get_top_valued_items(organization, limit=5)
        ctx["value_by_month"] = get_value_by_month(organization, months=6)

        return ctx
