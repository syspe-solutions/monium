from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.views import View

from apps.account.dtos.create_user_dto import CreateUserDTO
from apps.account.forms.auth import CustomRegisterForm
from apps.account.services.create_user_service import CreateUserService

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
