from django.urls import path

from .views import AdminSetupView, DatabaseSetupView

app_name = "setup"

urlpatterns = [
    path("database/", DatabaseSetupView.as_view(), name="database"),
    path("admin/", AdminSetupView.as_view(), name="admin"),
]
