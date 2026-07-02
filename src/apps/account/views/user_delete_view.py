from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from apps.account.models import User


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "account/profile/profile_delete_confirm.html"
    success_url = reverse_lazy("account:login")

    def get_object(self, queryset=None):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        logout(request)
        return super().delete(request, *args, **kwargs)
