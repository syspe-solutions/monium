from django.conf import settings
from django.db import migrations


def backfill_missing_subscriptions(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    Subscription = apps.get_model("billing", "Subscription")

    for user in User.objects.filter(subscription__isnull=True):
        Subscription.objects.create(user=user, plan_id="free")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0004_remove_subscription_organization_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(backfill_missing_subscriptions, noop),
    ]
