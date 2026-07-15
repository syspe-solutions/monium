from django.db import migrations

PLAN_ORDER = ["free", "starter", "pro", "enterprise"]


def _plan_rank(plan_id):
    try:
        return PLAN_ORDER.index(plan_id)
    except ValueError:
        return 0


def backfill_subscription_user(apps, schema_editor):
    Subscription = apps.get_model("billing", "Subscription")
    Membership = apps.get_model("organizations", "Membership")

    for subscription in Subscription.objects.filter(user__isnull=True, organization__isnull=False):
        owner_membership = Membership.objects.filter(
            organization=subscription.organization, role="owner"
        ).order_by("created_at").first()
        if owner_membership is None:
            continue

        existing = Subscription.objects.filter(user=owner_membership.user_id).exclude(pk=subscription.pk).first()
        if existing is None:
            subscription.user_id = owner_membership.user_id
            subscription.save(update_fields=["user"])
        else:
            # Usuário já ficou com uma Subscription de outra organização nesse backfill:
            # mantém a de plano mais alto e descarta a outra.
            if _plan_rank(subscription.plan_id) > _plan_rank(existing.plan_id):
                existing.delete()
                subscription.user_id = owner_membership.user_id
                subscription.save(update_fields=["user"])
            else:
                subscription.delete()

    # Segurança: qualquer Subscription órfã (organização sem dono encontrado, ou
    # sem organização) que ainda não tenha usuário não pode sobreviver à
    # próxima migration, que torna o campo obrigatório.
    Subscription.objects.filter(user__isnull=True).delete()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0002_subscription_user_alter_subscription_organization"),
    ]

    operations = [
        migrations.RunPython(backfill_subscription_user, noop),
    ]
