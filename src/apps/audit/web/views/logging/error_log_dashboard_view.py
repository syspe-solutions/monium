from apps.audit.web.views.logging.log_dashboard_base_view import BaseLayerDashboardView


class ErrorLogDashboardView(BaseLayerDashboardView):
    layer = "error"
    template_name = "audit/log_dashboard_error.html"
    empty_colspan = 4
