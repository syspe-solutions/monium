from .plans import PLANS_BY_ID


def get_plan(plan_id: str) -> dict:
    return PLANS_BY_ID.get(plan_id, PLANS_BY_ID["free"])


def get_subscription(organization):
    if organization is None:
        return None
    return getattr(organization, "subscription", None)


def get_plan_for_organization(organization) -> dict:
    subscription = get_subscription(organization)
    plan_id = subscription.plan_id if subscription else "free"
    return get_plan(plan_id)


def get_items_count(organization) -> int:
    from apps.inventory.models import Item

    return Item.objects.filter(organization=organization).count()


def is_within_item_limit(organization) -> bool:
    plan = get_plan_for_organization(organization)
    limit = plan["item_limit"]
    if limit is None:
        return True
    return get_items_count(organization) < limit


def has_feature(organization, feature: str) -> bool:
    plan = get_plan_for_organization(organization)
    return feature in plan["capabilities"]


def get_owned_organizations(user):
    from apps.organizations.models import MembershipRole, Organization

    return Organization.objects.filter(memberships__user=user, memberships__role=MembershipRole.OWNER)


def get_best_owned_plan(user) -> dict:
    """Maior org_limit entre os planos das organizações que o usuário possui (dono)."""
    plans = [get_plan_for_organization(org) for org in get_owned_organizations(user)]
    if not plans:
        return get_plan("free")

    unlimited = next((plan for plan in plans if plan["org_limit"] is None), None)
    if unlimited:
        return unlimited
    return max(plans, key=lambda plan: plan["org_limit"])


def can_create_organization(user) -> bool:
    owned_count = get_owned_organizations(user).count()
    if owned_count == 0:
        return True

    limit = get_best_owned_plan(user)["org_limit"]
    if limit is None:
        return True
    return owned_count < limit
