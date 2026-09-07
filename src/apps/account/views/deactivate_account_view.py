from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.views import View

from apps.account.models import UserDeletionSchedule


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
