from unittest import mock
from unittest.mock import patch, MagicMock

from django.http import HttpResponse
from django.test import SimpleTestCase
from django.test.client import RequestFactory

from apps.audit.view_logging_middleware import ProjectViewLoggingMiddleware


class ProjectViewLoggingMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _middleware(self, status_code: int):
        def get_response(_request):
            return HttpResponse(status=status_code)

        return ProjectViewLoggingMiddleware(get_response)

    @patch("apps.audit.view_logging_middleware.AccessLogger.log_event")
    @patch("apps.audit.view_logging_middleware.SecurityLogger.log_event")
    @patch('apps.audit.view_logging_middleware.ErrorLogger.log_event')
    def test_access_log_is_emitted(self, error_log, security_log, access_log):
        request = self.factory.post("/business/solicitations/")
        response = self._middleware(201)(request)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(access_log.called)
        self.assertFalse(security_log.called)
        self.assertFalse(error_log.called)

    @patch("apps.audit.view_logging_middleware.AccessLogger.log_event")
    @patch("apps.audit.view_logging_middleware.SecurityLogger.log_event")
    @patch('apps.audit.view_logging_middleware.ErrorLogger.log_event')
    def test_security_status_logs_security(self, error_log, security_log, access_log):
        request = self.factory.get("/account/login/")
        response = self._middleware(403)(request)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(access_log.called)
        self.assertTrue(security_log.called)
        self.assertFalse(error_log.called)

    @patch("apps.audit.view_logging_middleware.AccessLogger.log_event")
    @patch("apps.audit.view_logging_middleware.SecurityLogger.log_event")
    @patch('apps.audit.view_logging_middleware.ErrorLogger.log_event')
    def test_server_error_logs_error_layer(self, error_log, security_log, access_log):
        # 1. Garante que o path NÃO está nos ignorados
        request = self.factory.get('/api/resource/')

        # 2. Simula uma resposta 500
        get_response = MagicMock()
        get_response.return_value.status_code = 500

        middleware = ProjectViewLoggingMiddleware(get_response)
        middleware(request)

        # 3. Verifica se o ErrorLogger foi chamado (e não o SecurityLogger)
        self.assertTrue(error_log.called)
        self.assertFalse(security_log.called)

        error_log.assert_called_with(
            error_type=mock.ANY,
            message=mock.ANY,
            context=mock.ANY,
        )