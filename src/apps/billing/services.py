from .plans import PLANS_BY_ID


def get_plan(plan_id: str) -> dict:
    return PLANS_BY_ID.get(plan_id, PLANS_BY_ID["free"])


def get_subscription(user):
    if user is None:
        return None
    return getattr(user, "subscription", None)


def get_plan_for_user(user) -> dict:
    subscription = get_subscription(user)
    plan_id = subscription.plan_id if subscription else "free"
    return get_plan(plan_id)


def get_organization_owner(organization):
    """Toda organização tem exatamente um dono (criada com role=owner na criação)."""
    if organization is None:
        return None

    from apps.organizations.models import MembershipRole

    membership = (
        organization.memberships.filter(role=MembershipRole.OWNER).select_related("user").first()
    )
    return membership.user if membership else None


def get_plan_for_organization(organization) -> dict:
    """O plano de uma organização é sempre o da assinatura do seu dono —
    quem paga assina uma vez e o plano vale integralmente para cada organização dele."""
    return get_plan_for_user(get_organization_owner(organization))


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


def can_create_organization(user) -> bool:
    limit = get_plan_for_user(user)["org_limit"]
    if limit is None:
        return True
    return get_owned_organizations(user).count() < limit


def get_locked_organizations(user):
    """Organizações que o usuário possui além do org_limit do seu plano atual —
    as mais antigas continuam ativas, as mais recentes (excedentes) ficam bloqueadas."""
    limit = get_plan_for_user(user)["org_limit"]
    owned = list(get_owned_organizations(user).order_by("created_at"))
    if limit is None or len(owned) <= limit:
        return []
    return owned[limit:]


def is_organization_locked(organization) -> bool:
    owner = get_organization_owner(organization)
    if owner is None:
        return False
    locked_ids = {org.id for org in get_locked_organizations(owner)}
    return organization.id in locked_ids


def get_members_count(organization) -> int:
    return organization.memberships.count()


def is_within_user_limit(organization) -> bool:
    plan = get_plan_for_organization(organization)
    limit = plan["user_limit"]
    if limit is None:
        return True
    return get_members_count(organization) < limit


def is_within_user_limit_including_pending(organization) -> bool:
    """Usado ao enviar um convite: conta membros atuais + convites já pendentes,
    pra não deixar o dono mandar vários convites simultâneos todos "dentro do limite"."""
    from apps.organizations.models import InvitationStatus

    plan = get_plan_for_organization(organization)
    limit = plan["user_limit"]
    if limit is None:
        return True

    pending = organization.invitations.filter(status=InvitationStatus.PENDING).count()
    return get_members_count(organization) + pending < limit
