from django.urls import path

from .views import (
    MemberCreateView,
    MemberRemoveView,
    MemberRoleUpdateView,
    OrganizationCreateView,
    OrganizationDeleteView,
    OrganizationOnboardingView,
    OrganizationSettingsView,
    SwitchOrganizationView,
)

app_name = "organizations"

urlpatterns = [
    path("create/", OrganizationCreateView.as_view(), name="create"),
    path("onboarding/", OrganizationOnboardingView.as_view(), name="onboarding"),
    path("switch/<uuid:organization_id>/", SwitchOrganizationView.as_view(), name="switch"),
    path("settings/", OrganizationSettingsView.as_view(), name="settings"),
    path("members/create/", MemberCreateView.as_view(), name="member_create"),
    path("members/<uuid:membership_id>/remove/", MemberRemoveView.as_view(), name="member_remove"),
    path("members/<uuid:membership_id>/role/", MemberRoleUpdateView.as_view(), name="member_role_update"),
    path("<uuid:organization_id>/delete/", OrganizationDeleteView.as_view(), name="delete"),
]
