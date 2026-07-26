from django.test import TestCase

from apps.settings.exceptions import EmailNotConfiguredError
from apps.settings.models import EmailSettings
from apps.settings.services.email_configuration_resolver_service import (
    EmailConfigurationResolverService,
)


class EmailConfigurationResolverServiceTests(TestCase):
    def setUp(self):
        self.resolver = EmailConfigurationResolverService()

    def test_raises_when_no_configuration_exists(self):
        with self.assertRaises(EmailNotConfiguredError):
            self.resolver.resolve()

    def test_raises_when_configuration_is_disabled(self):
        EmailSettings.objects.create(is_enabled=False, host="smtp.example.com")
        with self.assertRaises(EmailNotConfiguredError):
            self.resolver.resolve()

    def test_raises_when_enabled_but_host_is_blank(self):
        EmailSettings.objects.create(is_enabled=True, host="")
        with self.assertRaises(EmailNotConfiguredError):
            self.resolver.resolve()

    def test_resolves_database_configuration_when_enabled_and_host_is_set(self):
        EmailSettings.objects.create(
            is_enabled=True,
            host="db-smtp.example.com",
            port=587,
            use_tls=True,
            host_user="db-user",
            host_password="db-password",
            default_from_email="db-default@example.com",
        )

        configuration = self.resolver.resolve()

        self.assertEqual(configuration.host, "db-smtp.example.com")
        self.assertEqual(configuration.port, 587)
        self.assertTrue(configuration.use_tls)
        self.assertEqual(configuration.username, "db-user")
        self.assertEqual(configuration.password, "db-password")
        self.assertEqual(configuration.default_from_email, "db-default@example.com")
