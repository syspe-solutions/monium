from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.organizations.models import Organization

from .models import Subscription


@receiver(post_save, sender=Organization)
def create_free_subscription_for_new_organization(sender, instance, created, **kwargs):
    if not created:
        return
    Subscription.objects.get_or_create(organization=instance, defaults={"plan_id": "free"})
