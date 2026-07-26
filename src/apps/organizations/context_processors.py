from .models import MembershipRole, Organization


def organization_context(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}

    organization = getattr(request, "organization", None)
    if organization is None:
        return {"current_organization": None}

    membership = user.memberships.filter(organization=organization).first()
    user_organizations = list(
        Organization.objects.filter(memberships__user=user)
        .order_by("memberships__created_at")
        .distinct()
    )
    owner_organization_ids = set(
        user.memberships.filter(role=MembershipRole.OWNER).values_list("organization_id", flat=True)
    )

    return {
        "current_organization": organization,
        "is_organization_owner": bool(membership and membership.role == MembershipRole.OWNER),
        "can_manage_members": bool(membership and membership.can_manage_members()),
        "user_organizations": user_organizations,
        "owner_organization_ids": owner_organization_ids,
        "has_multiple_organizations": len(user_organizations) > 1,
    }
