from apps.audit.web.views.logging.log_dashboard_base_view import BaseLayerDashboardView


class AccessLogDashboardView(BaseLayerDashboardView):
    layer = "access"
    template_name = "audit/log_dashboard_access.html"
    empty_colspan = 6
