from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.account.dtos.login_user_dto import LoginUserDTO
from apps.account.forms.auth import CustomLoginForm
from apps.account.services.login_user_service import LoginUserService
from apps.twofactor.models import TwoFactorDevice
from apps.twofactor.services import TwoFactorLoginChallengeService


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

        next_url = request.POST.get("next") or request.GET.get("next")

        if TwoFactorDevice.objects.filter(user=result.user, confirmed=True).exists():
            TwoFactorLoginChallengeService.start(request, result.user, next_url or "")
            return redirect("twofactor:login_verify")

        login(request, result.user)

        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("inventory:home")

    def _handle_error(self, request, error_code):
        errors = {
            "invalid_credentials": _("Usuário ou senha inválidos."),
            "inactive_user": _("Sua conta foi encerrada."),
        }
        messages.error(request, errors.get(
            error_code, _("Erro inesperado.")))
