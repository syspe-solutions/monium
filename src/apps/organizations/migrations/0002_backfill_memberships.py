import uuid

from django.conf import settings
from django.db import migrations


def backfill_organizations(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    Organization = apps.get_model("organizations", "Organization")
    Membership = apps.get_model("organizations", "Membership")
    Subscription = apps.get_model("billing", "Subscription")

    for user in User.objects.exclude(memberships__isnull=False):
        display_name = f"{user.first_name} {user.last_name}".strip() or user.username
        organization = Organization.objects.create(
            name=display_name,
            slug=f"org-{uuid.uuid4().hex[:12]}",
            created_by=user,
        )
        Membership.objects.create(organization=organization, user=user, role="owner", created_by=user)
        Subscription.objects.get_or_create(organization=organization, defaults={"plan_id": "free"})


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0001_initial"),
        ("billing", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(backfill_organizations, noop),
    ]
