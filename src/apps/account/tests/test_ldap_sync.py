from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.test import RequestFactory, TestCase, override_settings

from apps.organizations.models import Membership, MembershipRole, Organization

User = get_user_model()


def create_organization(slug="empresa"):
    return Organization.objects.create(
        name="Empresa", slug=slug,
        industry="technology", size="1-10", primary_goal="it_equipment",
    )


def fire_ldap_login(user, group_names):
    user.ldap_user = SimpleNamespace(group_names=set(group_names))
    user_logged_in.send(sender=user.__class__, request=RequestFactory().get("/"), user=user)


class LdapMembershipSyncTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="ldapuser", email="ldap@example.com")
        self.organization = create_organization()

    def test_no_target_organization_configured_does_nothing(self):
        with override_settings(LDAP_TARGET_ORGANIZATION_SLUG=""):
            fire_ldap_login(self.user, {"admins"})

        self.assertFalse(Membership.objects.filter(user=self.user).exists())

    def test_non_ldap_login_is_ignored(self):
        with override_settings(LDAP_TARGET_ORGANIZATION_SLUG=self.organization.slug):
            user_logged_in.send(sender=self.user.__class__, request=RequestFactory().get("/"), user=self.user)

        self.assertFalse(Membership.objects.filter(user=self.user).exists())

    def test_creates_membership_with_matched_admin_group(self):
        with override_settings(
            LDAP_TARGET_ORGANIZATION_SLUG=self.organization.slug,
            LDAP_ROLE_GROUPS_ADMIN={"admins"},
        ):
            fire_ldap_login(self.user, {"admins", "everyone"})

        membership = Membership.objects.get(user=self.user, organization=self.organization)
        self.assertEqual(membership.role, MembershipRole.ADMIN)

    def test_falls_back_to_default_role_when_no_group_matches(self):
        with override_settings(
            LDAP_TARGET_ORGANIZATION_SLUG=self.organization.slug,
            LDAP_ROLE_GROUPS_ADMIN={"admins"},
            LDAP_DEFAULT_ROLE=MembershipRole.OPERATOR,
        ):
            fire_ldap_login(self.user, {"everyone"})

        membership = Membership.objects.get(user=self.user, organization=self.organization)
        self.assertEqual(membership.role, MembershipRole.OPERATOR)

    def test_never_downgrades_existing_owner(self):
        Membership.objects.create(
            user=self.user, organization=self.organization, role=MembershipRole.OWNER
        )

        with override_settings(
            LDAP_TARGET_ORGANIZATION_SLUG=self.organization.slug,
            LDAP_ROLE_GROUPS_OPERATOR={"staff"},
        ):
            fire_ldap_login(self.user, {"staff"})

        membership = Membership.objects.get(user=self.user, organization=self.organization)
        self.assertEqual(membership.role, MembershipRole.OWNER)

    def test_unknown_target_organization_is_ignored(self):
        with override_settings(LDAP_TARGET_ORGANIZATION_SLUG="does-not-exist"):
            fire_ldap_login(self.user, {"admins"})

        self.assertFalse(Membership.objects.filter(user=self.user).exists())
