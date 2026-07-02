from django.urls import path

from apps.audit.web.views.audit_data_view import AuditDataView
from apps.audit.web.views.logging.log_export_view import LogExportView
from apps.audit.web.views.logging.log_layer_dashboard_view import LogLayerDashboardView
from apps.audit.web.views.logging.log_layer_list_view import LogLayerListView
from apps.audit.web.views.logging.log_metrics_view import LogMetricsView

app_name = 'audit'

urlpatterns = [
    path('dashboard/<str:layer>/', LogLayerDashboardView.as_view(), name='log-layer-dashboard'),
    path('data/', AuditDataView.as_view(), name='audit-data'),

    path('logs/<str:layer>/', LogLayerListView.as_view(), name='log-layer-list'),
    path('logs/<str:layer>/export/', LogExportView.as_view(), name='log-export'),
    path('logs/<str:layer>/metrics/', LogMetricsView.as_view(), name='log-metrics'),
]
