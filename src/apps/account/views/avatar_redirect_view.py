from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import View

from apps.account.models import UserProfile


class AvatarRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(UserProfile, user_id=kwargs.get('user_id'))

        if profile.user != request.user and not request.user.is_superuser:
            return HttpResponseForbidden("Você não tem permissão para visualizar esta imagem.")

        if not profile.avatar:
            return HttpResponseRedirect('/static/images/default-avatar.png')
        return HttpResponseRedirect(profile.avatar.url)
