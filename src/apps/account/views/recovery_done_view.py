from django.contrib.auth.views import PasswordResetDoneView


class RecoveryDoneView(PasswordResetDoneView):
    template_name = "account/auth/password_reset_done.html"
