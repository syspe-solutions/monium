from django.urls import path

from .views import TwoFactorDisableView, TwoFactorLoginVerifyView, TwoFactorSetupView

app_name = "twofactor"

urlpatterns = [
    path("setup/", TwoFactorSetupView.as_view(), name="setup"),
    path("disable/", TwoFactorDisableView.as_view(), name="disable"),
    path("verify/", TwoFactorLoginVerifyView.as_view(), name="login_verify"),
]
