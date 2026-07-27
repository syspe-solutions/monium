from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from apps.organizations.models import Organization


@receiver(post_delete, sender=Organization)
def delete_logo_on_delete(sender, instance, **kwargs):
    if instance.logo:
        instance.logo.delete(save=False)


@receiver(pre_save, sender=Organization)
def delete_old_logo_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_organization = Organization.objects.get(pk=instance.pk)
    except Organization.DoesNotExist:
        return

    old_logo = old_organization.logo
    new_logo = instance.logo

    if old_logo and old_logo != new_logo:
        old_logo.delete(save=False)
