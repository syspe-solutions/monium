from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as translate
from django.views import View

from apps.account.dtos.create_user_dto import CreateUserDTO
from apps.account.dtos.login_user_dto import LoginUserDTO
from apps.account.forms.auth import CustomLoginForm, CustomRegisterForm
from apps.account.models import UserDeletionSchedule
from apps.account.services.create_user_service import CreateUserService
from apps.account.services.login_user_service import LoginUserService

User = get_user_model()


class UserRegisterView(View):
    template_name = "account/auth/register.html"

    def get(self, request):
        return render(request, self.template_name, {'form': CustomRegisterForm()})

    def post(self, request):
        if settings.DEBUG and request.headers.get("X-CYPRESS") == "true":
            User.objects.filter(email="cypress@test.com").delete()
            User.objects.filter(username="cypress").delete()

        form = CustomRegisterForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        try:
            dto = CreateUserDTO(**form.cleaned_data)
            CreateUserService.execute(dto)
            print("REGISTER POST HIT:", datetime.now(), request.META.get("REMOTE_ADDR"))
            return redirect("account:login")

        except Exception as error:
            raise error


class UserLoginView(View):
    template_name = "account/auth/login.html"
    form_class = CustomLoginForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("inventory:home")
        return render(request, self.template_name, {"form": self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        dto = LoginUserDTO(**form.cleaned_data)
        result = LoginUserService.execute(request, dto)

        if not result.success:
            self._handle_error(request, result.error_code)
            return render(request, self.template_name, {"form": form}, status=400)

        login(request, result.user)
        return redirect("inventory:home")

    def _handle_error(self, request, error_code):
        errors = {
            "invalid_credentials": translate("Usuário ou senha inválidos."),
            "inactive_user": translate("Sua conta foi encerrada."),
        }
        messages.error(request, errors.get(
            error_code, translate("Erro inesperado.")))


class UserLogoutView(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        logout(request)
        return redirect("account:login")


class RecoveryView(PasswordResetView):
    template_name = "account/auth/password_reset.html"
    email_template_name = "notification/email/password_reset.html"
    html_email_template_name = "notification/email/password_reset.html"
    subject_template_name = "account/auth/password_reset_subject.txt"
    success_url = reverse_lazy("account:password_reset_done")


class RecoveryDoneView(PasswordResetDoneView):
    template_name = "account/auth/password_reset_done.html"


class RecoveryConfirmView(PasswordResetConfirmView):
    template_name = "account/auth/password_reset_confirm.html"
    success_url = reverse_lazy("account:password_reset_complete")


class RecoveryCompleteView(PasswordResetCompleteView):
    template_name = "account/auth/password_reset_complete.html"


class DeactivateAccount(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        user.is_active = False
        user.save()

        UserDeletionSchedule.objects.update_or_create(
            user=user,
            defaults={
                "scheduled_for": timezone.now() + timedelta(days=30)
            }
        )

        return redirect("account:logout")
