from apps.audit.web.views.logging.log_dashboard_base_view import BaseLayerDashboardView


class SecurityLogDashboardView(BaseLayerDashboardView):
    layer = "security"
    template_name = "audit/log_dashboard_security.html"
    empty_colspan = 6
