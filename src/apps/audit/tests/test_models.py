from django.test import TestCase

from apps.audit.models import Audit


class AuditTestCase(TestCase):
    def setUp(self):
        self.audit = Audit.objects.create(
            total_time=1.25,
            python_time=0.75,
            db_time=0.50,
            total_queries=12,
            path="/api/v1/test/",
            method="GET",
            host="localhost",
            port=8000,
            content_type="application/json",
            body='{"key": "value"}',
            user_agent="Mozilla/5.0",
            response_content='{"status": "ok"}',
            response_status_code=200,
            ip="127.0.0.1",
            proxy_verified=True,
        )

    def test_audit_was_created(self):
        self.assertEqual(Audit.objects.count(), 1)
        self.assertEqual(self.audit.method, "GET")
        self.assertEqual(self.audit.response_status_code, 200)

    def test_audit_str_representation(self):
        self.assertIn("Auditor:", str(self.audit))

    def test_audit_nullable_fields(self):
        audit_null = Audit.objects.create(
            total_time=2.0,
            python_time=1.0,
            db_time=1.0,
            total_queries=5,
            path="/api/v1/null-fields/",
            method="POST",
            host="127.0.0.1"
        )
        self.assertIsNone(audit_null.port)
        self.assertIsNone(audit_null.content_type)
        self.assertIsNone(audit_null.body)
        self.assertIsNone(audit_null.user_agent)
        self.assertIsNone(audit_null.response_content)
        self.assertIsNone(audit_null.response_status_code)
        self.assertIsNone(audit_null.ip)
        self.assertIsNone(audit_null.proxy_verified)
