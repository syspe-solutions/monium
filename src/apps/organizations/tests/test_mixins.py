from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from apps.audit.dtos import SecurityAction, SecurityStatus
from apps.organizations.mixins import (
    InventoryWriteRequiredMixin,
    MemberManagementRequiredMixin,
    OrganizationOwnerRequiredMixin,
)
from apps.organizations.models import Membership, MembershipRole, Organization

User = get_user_model()


def build_request(user, organization=None):
    request = RequestFactory().get("/")
    request.user = user
    request.organization = organization
    return request


def create_organization_with_member(user, role):
    organization = Organization.objects.create(
        name="Test Org", slug=f"test-org-{user.username}",
        industry="technology", size="1-10", primary_goal="it_equipment",
    )
    Membership.objects.create(organization=organization, user=user, role=role)
    return organization


class _MembershipRoleRequiredMixinCases:
    """Cenários padrão de `_MembershipRoleRequiredMixin.test_func`, parametrizados por
    subclasse via `mixin_class`/`allowed_role`/`disallowed_role`. Não herda de TestCase
    para não ser coletada como suíte própria — só as subclasses concretas são."""

    mixin_class = None
    allowed_role = None
    disallowed_role = None

    def _build_mixin(self, request):
        mixin = self.mixin_class()
        mixin.request = request
        return mixin

    def test_anonymous_user_is_denied(self):
        request = build_request(AnonymousUser())
        self.assertFalse(self._build_mixin(request).test_func())

    def test_user_without_active_organization_is_denied(self):
        user = User.objects.create_user(username=f"no-org-{self.mixin_class.__name__}", password="12345")
        request = build_request(user, organization=None)
        self.assertFalse(self._build_mixin(request).test_func())

    def test_user_with_disallowed_role_is_denied(self):
        user = User.objects.create_user(username=f"wrong-role-{self.mixin_class.__name__}", password="12345")
        organization = create_organization_with_member(user, self.disallowed_role)
        request = build_request(user, organization=organization)
        self.assertFalse(self._build_mixin(request).test_func())

    def test_user_with_allowed_role_is_granted(self):
        user = User.objects.create_user(username=f"right-role-{self.mixin_class.__name__}", password="12345")
        organization = create_organization_with_member(user, self.allowed_role)
        request = build_request(user, organization=organization)
        self.assertTrue(self._build_mixin(request).test_func())

    @patch("apps.organizations.mixins.SecurityLogger.log_event")
    def test_denied_access_logs_security_event(self, mock_log_event):
        request = build_request(AnonymousUser())
        self._build_mixin(request).test_func()

        mock_log_event.assert_called_once()
        _, kwargs = mock_log_event.call_args
        self.assertEqual(kwargs["action"], SecurityAction.UNAUTHORIZED_ACCESS)
        self.assertEqual(kwargs["status"], SecurityStatus.FAILED)


class OrganizationOwnerRequiredMixinTests(_MembershipRoleRequiredMixinCases, TestCase):
    mixin_class = OrganizationOwnerRequiredMixin
    allowed_role = MembershipRole.OWNER
    disallowed_role = MembershipRole.ADMIN


class MemberManagementRequiredMixinTests(_MembershipRoleRequiredMixinCases, TestCase):
    mixin_class = MemberManagementRequiredMixin
    allowed_role = MembershipRole.ADMIN
    disallowed_role = MembershipRole.MANAGER


class InventoryWriteRequiredMixinTests(_MembershipRoleRequiredMixinCases, TestCase):
    mixin_class = InventoryWriteRequiredMixin
    allowed_role = MembershipRole.OPERATOR
    disallowed_role = MembershipRole.VIEWER
