from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Subscription

User = get_user_model()


@receiver(post_save, sender=User)
def create_free_subscription_for_new_user(sender, instance, created, **kwargs):
    if not created:
        return
    Subscription.objects.get_or_create(user=instance, defaults={"plan_id": "free"})
