from apps.audit.web.views.logging.log_dashboard_base_view import BaseLayerDashboardView


class BusinessLogDashboardView(BaseLayerDashboardView):
    layer = "business"
    template_name = "audit/log_dashboard_business.html"
    empty_colspan = 5
