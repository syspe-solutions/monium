from apps.audit.web.views.logging.log_dashboard_base_view import BaseLayerDashboardView


class CeleryLogDashboardView(BaseLayerDashboardView):
    layer = "celery"
    template_name = "audit/log_dashboard_celery.html"
    empty_colspan = 6
