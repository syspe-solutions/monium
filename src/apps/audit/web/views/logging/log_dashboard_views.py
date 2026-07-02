from apps.audit.web.views.logging.log_dashboard_base_view import BaseLayerDashboardView


class BusinessLogDashboardView(BaseLayerDashboardView):
    layer = "business"
    template_name = "audit/log_dashboard_business.html"
    empty_colspan = 5


class AccessLogDashboardView(BaseLayerDashboardView):
    layer = "access"
    template_name = "audit/log_dashboard_access.html"
    empty_colspan = 6


class SecurityLogDashboardView(BaseLayerDashboardView):
    layer = "security"
    template_name = "audit/log_dashboard_security.html"
    empty_colspan = 6


class PerformanceLogDashboardView(BaseLayerDashboardView):
    layer = "performance"
    template_name = "audit/log_dashboard_performance.html"
    empty_colspan = 6


class ErrorLogDashboardView(BaseLayerDashboardView):
    layer = "error"
    template_name = "audit/log_dashboard_error.html"
    empty_colspan = 4


class CeleryLogDashboardView(BaseLayerDashboardView):
    layer = "celery"
    template_name = "audit/log_dashboard_celery.html"
    empty_colspan = 6


class DatabaseLogDashboardView(BaseLayerDashboardView):
    layer = "database"
    template_name = "audit/log_dashboard_database.html"
    empty_colspan = 6
