from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from apps.account.models import UserProfile


@receiver(post_delete, sender=UserProfile)
def delete_s3_avatar_on_delete(sender, instance, **kwargs):
    if instance.avatar:
        instance.avatar.delete(save=False)


@receiver(pre_save, sender=UserProfile)
def delete_old_s3_avatar_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_profile = UserProfile.objects.get(pk=instance.pk)
    except UserProfile.DoesNotExist:
        return

    old_avatar = old_profile.avatar
    new_avatar = instance.avatar

    if old_avatar and old_avatar != new_avatar:
        old_avatar.delete(save=False)
