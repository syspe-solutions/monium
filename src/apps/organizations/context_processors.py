from .models import MembershipRole, Organization


def organization_context(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}

    from apps.billing import services as billing_services

    locked_organizations = billing_services.get_locked_organizations(user)

    organization = getattr(request, "organization", None)
    if organization is None:
        return {"current_organization": None, "locked_organizations": locked_organizations}

    membership = user.memberships.filter(organization=organization).first()
    user_organizations = list(
        Organization.objects.filter(memberships__user=user)
        .order_by("memberships__created_at")
        .distinct()
    )

    return {
        "current_organization": organization,
        "is_organization_owner": bool(membership and membership.role == MembershipRole.OWNER),
        "user_organizations": user_organizations,
        "has_multiple_organizations": len(user_organizations) > 1,
        "locked_organizations": locked_organizations,
    }
