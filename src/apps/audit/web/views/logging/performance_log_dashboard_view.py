from apps.audit.web.views.logging.log_dashboard_base_view import BaseLayerDashboardView


class PerformanceLogDashboardView(BaseLayerDashboardView):
    layer = "performance"
    template_name = "audit/log_dashboard_performance.html"
    empty_colspan = 6
