from django.urls import path

from .views import (
    InvitationAcceptView,
    InvitationCreateView,
    InvitationRevokeView,
    MemberRemoveView,
    OrganizationCreateView,
    OrganizationDeleteView,
    OrganizationMembersView,
    OrganizationSettingsView,
    SwitchOrganizationView,
)

app_name = "organizations"

urlpatterns = [
    path("create/", OrganizationCreateView.as_view(), name="create"),
    path("switch/<uuid:organization_id>/", SwitchOrganizationView.as_view(), name="switch"),
    path("settings/", OrganizationSettingsView.as_view(), name="settings"),
    path("members/", OrganizationMembersView.as_view(), name="members"),
    path("members/invite/", InvitationCreateView.as_view(), name="invite_create"),
    path("members/<uuid:membership_id>/remove/", MemberRemoveView.as_view(), name="member_remove"),
    path("invitations/<uuid:invitation_id>/revoke/", InvitationRevokeView.as_view(), name="invitation_revoke"),
    path("invitations/accept/<str:token>/", InvitationAcceptView.as_view(), name="invitation_accept"),
    path("<uuid:organization_id>/delete/", OrganizationDeleteView.as_view(), name="delete"),
]
