import tempfile
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.inventory.models import Acquisition, Brand, Category, ImovelCategory, Movel, MovelSpec, Sector
from apps.organizations.models import Membership, Organization

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class DemoDataCommandsTest(TestCase):
    def test_populate_creates_demo_organization_with_items_photos_and_values(self):
        user = User.objects.create_user(username="demo_owner", email="demo@example.com", password="x")

        call_command("populate_demo_data", stdout=StringIO())

        organization = Organization.objects.get(slug="organizacao-demo")
        self.assertTrue(Membership.objects.filter(user=user, organization=organization).exists())

        items = Movel.objects.filter(organization=organization)
        self.assertGreater(items.count(), 0)

        for item in items:
            spec = MovelSpec.objects.get(movel=item)
            self.assertTrue(spec.image)
            acquisition = Acquisition.objects.get(item=item)
            self.assertIsNotNone(acquisition.value)

    def test_populate_is_idempotent(self):
        User.objects.create_user(username="demo_owner2", email="demo2@example.com", password="x")
        call_command("populate_demo_data", stdout=StringIO())
        first_count = Movel.objects.count()

        call_command("populate_demo_data", stdout=StringIO())
        second_count = Movel.objects.count()

        self.assertEqual(first_count, second_count)

    def test_clear_removes_everything_populate_created(self):
        User.objects.create_user(username="demo_owner3", email="demo3@example.com", password="x")
        call_command("populate_demo_data", stdout=StringIO())

        call_command("clear_demo_data", stdout=StringIO())

        self.assertFalse(Organization.objects.filter(slug="organizacao-demo").exists())
        self.assertFalse(Category.objects.filter(slug__startswith="demo-").exists())
        self.assertFalse(Sector.objects.filter(slug__startswith="demo-").exists())
        self.assertFalse(Brand.objects.filter(slug__startswith="demo-").exists())
        self.assertFalse(ImovelCategory.objects.filter(slug__startswith="demo-").exists())
        self.assertFalse(Movel.objects.filter(code__startswith="DEMO-").exists())

    def test_clear_does_not_touch_other_organizations(self):
        real_org = Organization.objects.create(name="Empresa Real", slug="empresa-real")
        User.objects.create_user(username="demo_owner4", email="demo4@example.com", password="x")

        call_command("populate_demo_data", stdout=StringIO())
        call_command("clear_demo_data", stdout=StringIO())

        self.assertTrue(Organization.objects.filter(pk=real_org.pk).exists())

    def test_clear_with_no_demo_data_is_a_noop(self):
        out = StringIO()
        call_command("clear_demo_data", stdout=out)
        self.assertIn("Nenhuma organização demo encontrada", out.getvalue())
