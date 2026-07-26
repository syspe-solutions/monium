from django.urls import path

from .views import EmailSettingsView

app_name = "settings"

urlpatterns = [
    path("email/", EmailSettingsView.as_view(), name="email_settings"),
]
