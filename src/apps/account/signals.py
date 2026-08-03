from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from apps.account.models import UserProfile
from apps.organizations.models import Membership, MembershipRole, Organization

_LDAP_ROLE_PRIORITY = [
    (MembershipRole.ADMIN, "LDAP_ROLE_GROUPS_ADMIN"),
    (MembershipRole.MANAGER, "LDAP_ROLE_GROUPS_MANAGER"),
    (MembershipRole.OPERATOR, "LDAP_ROLE_GROUPS_OPERATOR"),
]


def resolve_ldap_role(group_names: set) -> str:
    for role, setting_name in _LDAP_ROLE_PRIORITY:
        if getattr(settings, setting_name, set()) & group_names:
            return role
    return getattr(settings, "LDAP_DEFAULT_ROLE", MembershipRole.VIEWER)


@receiver(user_logged_in)
def sync_ldap_membership(sender, request, user, **kwargs):
    ldap_user = getattr(user, "ldap_user", None)
    if ldap_user is None:
        return

    organization_slug = getattr(settings, "LDAP_TARGET_ORGANIZATION_SLUG", "")
    if not organization_slug:
        return

    try:
        organization = Organization.objects.get(slug=organization_slug)
    except Organization.DoesNotExist:
        return

    existing = Membership.objects.filter(user=user, organization=organization).first()
    if existing and existing.role == MembershipRole.OWNER:
        return

    role = resolve_ldap_role(set(ldap_user.group_names))
    Membership.objects.update_or_create(
        user=user, organization=organization, defaults={"role": role}
    )


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
