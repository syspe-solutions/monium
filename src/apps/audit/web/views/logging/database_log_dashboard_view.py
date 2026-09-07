from apps.audit.web.views.logging.log_dashboard_base_view import BaseLayerDashboardView


class DatabaseLogDashboardView(BaseLayerDashboardView):
    layer = "database"
    template_name = "audit/log_dashboard_database.html"
    empty_colspan = 6
