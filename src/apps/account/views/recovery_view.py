from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy


class RecoveryView(PasswordResetView):
    template_name = "account/auth/password_reset.html"
    email_template_name = "notification/email/password_reset.html"
    html_email_template_name = "notification/email/password_reset.html"
    subject_template_name = "account/auth/password_reset_subject.txt"
    success_url = reverse_lazy("account:password_reset_done")
