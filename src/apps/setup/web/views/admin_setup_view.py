from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View

from ..forms import AdminSetupForm


class AdminSetupView(View):
    template_name = "setup/admin.html"
    current_step = 2

    def get(self, request):
        self._guard_setup_still_pending()
        return render(request, self.template_name, self._context(AdminSetupForm()))

    def post(self, request):
        self._guard_setup_still_pending()

        form = AdminSetupForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._context(form))

        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("inventory:home")

    def _context(self, form):
        return {"form": form, "current_step": self.current_step}

    def _guard_setup_still_pending(self):
        if settings.DATABASE_SETUP_REQUIRED:
            raise Http404()
        if get_user_model().objects.filter(is_superuser=True).exists():
            raise Http404()
