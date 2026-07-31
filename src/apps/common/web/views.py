import os
import platform
import shutil
from datetime import datetime

import requests
from django.conf import settings
from django.core import signing
from django.http import HttpRequest, HttpResponse, JsonResponse, StreamingHttpResponse
from django.views import View

from apps.common.models import StoredFile
from apps.common.services.file_store_service import FileStoreService

SIGNED_URL_SALT = "file-proxy-private"
SIGNED_URL_MAX_AGE = 300  # 5 minutes


def generate_file_token(relative_path: str) -> str:
    return signing.dumps(relative_path, salt=SIGNED_URL_SALT)


class HealthCheckView(View):
    """
    Enhanced Health Check View (Requirement 5)
    Includes cache backend status and disk space availability.
    """
    def get(self, request):
        services = {
            "database": self._check_database(),
            "cache": self._check_cache(),
            "disk_logs": self._check_disk_space(),
            "file_store": self._check_file_store(),
        }
        
        is_healthy = all(s["status"] == "up" for s in services.values())
        
        health_data = {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "server": {
                "os": platform.system(),
                "release": platform.release(),
                "node": platform.node(),
            },
            "services": services
        }
        
        status_code = 200 if is_healthy else 503
        return JsonResponse(health_data, status=status_code)

    def _check_database(self):
        try:
            from django.db import connections
            db_conn = connections['default']
            db_conn.cursor()
            return {"status": "up"}
        except Exception as e:
            return {"status": "down", "error": str(e)}

    def _check_cache(self):
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', timeout=5)
            if cache.get('health_check') == 'ok':
                return {"status": "up", "backend": cache.__class__.__name__}
            return {"status": "down", "error": "Cache operations failed"}
        except Exception as e:
            return {"status": "down", "error": f"Cache error: {str(e)}"}

    def _check_file_store(self):
        try:
            data = FileStoreService().health_check()
            return {"status": "up", **data}
        except requests.Timeout:
            return {"status": "down", "error": "Timeout ao conectar ao serviço de armazenamento."}
        except requests.ConnectionError:
            return {"status": "down", "error": "Não foi possível conectar ao serviço de armazenamento."}
        except requests.HTTPError as exc:
            code = exc.response.status_code if exc.response is not None else "unknown"
            return {"status": "down", "error": f"Serviço de armazenamento retornou HTTP {code}."}
        except Exception as exc:
            return {"status": "down", "error": f"Erro inesperado: {exc}"}

    def _check_disk_space(self):
        try:
            log_dir = settings.LOG_DIR_WEB
            if not os.path.exists(log_dir):
                 os.makedirs(log_dir, exist_ok=True)
                 
            total, used, free = shutil.disk_usage(log_dir)
            
            return {
                "status": "up",
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "percent_free": round((free / total) * 100, 2)
            }
        except Exception as e:
            return {"status": "down", "error": f"Disk check error: {str(e)}"}


class FileProxyView(View):
    # private/{folder_type}/{user_id}/{filename}
    _PRIVATE_PREFIX = "private/"

    def get(self, request: HttpRequest, relative_path: str) -> HttpResponse:
        if relative_path.startswith(self._PRIVATE_PREFIX):
            if not self._authorized(request, relative_path):
                return HttpResponse(status=403)

        if not StoredFile.objects.filter(relative_path=relative_path).exists():
            return HttpResponse(status=404)

        response = FileStoreService().get_file(relative_path)
        if response is None:
            return HttpResponse(status=404)

        content_type = response.headers.get("Content-Type", self._guess_content_type(relative_path))
        return StreamingHttpResponse(
            streaming_content=self._stream(response),
            content_type=content_type,
        )

    @staticmethod
    def _authorized(request: HttpRequest, relative_path: str) -> bool:
        token = request.GET.get("sig")
        if token:
            try:
                signed_path = signing.loads(token, salt=SIGNED_URL_SALT, max_age=SIGNED_URL_MAX_AGE)
                return signed_path == relative_path
            except signing.BadSignature:
                return False

        if not request.user.is_authenticated:
            return False
        parts = relative_path.split("/")
        # parts: ["private", "<folder_type>", "<user_id>", "<filename>"]
        if len(parts) < 4:
            return False
        return str(request.user.pk) == parts[2]

    @staticmethod
    def _stream(response):
        try:
            yield from response.iter_content(chunk_size=8192)
        finally:
            response.close()

    @staticmethod
    def _guess_content_type(path: str) -> str:
        ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        return {
            "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "png": "image/png", "webp": "image/webp",
            "gif": "image/gif", "pdf": "application/pdf",
            "svg": "image/svg+xml",
        }.get(ext, "application/octet-stream")


# kept for backwards compatibility with existing imports
PublicFileProxyView = FileProxyView
