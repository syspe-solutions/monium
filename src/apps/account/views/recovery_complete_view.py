from django.contrib.auth.views import PasswordResetCompleteView


class RecoveryCompleteView(PasswordResetCompleteView):
    template_name = "account/auth/password_reset_complete.html"
