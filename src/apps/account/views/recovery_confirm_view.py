from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy


class RecoveryConfirmView(PasswordResetConfirmView):
    template_name = "account/auth/password_reset_confirm.html"
    success_url = reverse_lazy("account:password_reset_complete")
