from django.contrib import admin

from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan_id", "status", "current_period_end")
    list_filter = ("plan_id", "status")
    search_fields = ("user__username", "user__email")
