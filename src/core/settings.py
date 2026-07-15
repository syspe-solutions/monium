import os
import sys
from pathlib import Path

from dotenv import load_dotenv as loadenv

# ================================================================
# BASE DIRECTORIES
# ================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "apps"))
SITE_ID = 1

APPEND_SLASH = False

DOMAIN = os.environ.get("DJANGO_DOMAIN", "")
PROTOCOL = os.environ.get("DJANGO_PROTOCOL", "")
BACKEND_BASE_URL = os.environ.get("BACKEND_BASE_URL", "")

# ================================================================
# ENVIRONMENT VARIABLES
# ================================================================
loadenv(dotenv_path=BASE_DIR / ".env")


# ================================================================
# SECURITY
# ================================================================
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

DEBUG = True if os.environ.get("DJANGO_DEBUG", "FALSE") == "TRUE" else False


if DEBUG:
    ALLOWED_HOSTS = ["*"]
    CORS_ALLOW_ALL_ORIGINS = True
else:
    ALLOWED_HOSTS = [
        host
        for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
        if host
    ]
    CORS_ALLOWED_ORIGINS = [
        origin
        for origin in os.environ.get("DJANGO_CORS_ALLOWED_ORIGINS", "").split(",")
        if origin
    ]

CSRF_TRUSTED_ORIGINS = [
    origin
    for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin
]

SECURE_CROSS_ORIGIN_OPENER_POLICY = os.environ.get(
    "DJANGO_SECURE_CROSS_ORIGIN_OPENER_POLICY")

SECURE_SSL_REDIRECT = True if os.environ.get(
    "DJANGO_SECURE_SSL_REDIRECT") == "TRUE" else False


# ================================================================
# LOGGING
# ================================================================
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

LOG_DIR = os.path.join(BASE_DIR, os.environ.get("LOG_DIR", "logs"))
LOG_DIR_WEB = os.path.join(LOG_DIR, "web")
LOG_DIR_API = os.path.join(LOG_DIR, "api")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(LOG_DIR_WEB, exist_ok=True)
os.makedirs(LOG_DIR_API, exist_ok=True)

LOG_MAX_BYTES = 5 * 1024 * 1024  # 5MB
LOG_BACKUP_COUNT = 5

def get_file_handler(filename, formatter="json"):
    return {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(LOG_DIR_WEB, filename),
        "maxBytes": LOG_MAX_BYTES,
        "backupCount": LOG_BACKUP_COUNT,
        "formatter": formatter,
        "encoding": "utf-8",
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "core.utilities.structured_logging.StructuredJSONFormatter",
        },
        "console_dev": {
            "format": "[{levelname}] {asctime} {name} - {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "business_file": get_file_handler("business.log"),
        "access_file": get_file_handler("access.log"),
        "error_file": get_file_handler("error.log"),
        "security_file": get_file_handler("security.log"),
        "database_file": get_file_handler("database.log"),
        "celery_file": get_file_handler("celery.log"),
        "performance_file": get_file_handler("performance.log"),
        "websocket": {
            "class": "core.utilities.structured_logging.WebSocketHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console", "error_file"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["access_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["database_file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "business": {
            "handlers": ["business_file", "websocket"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.security": {
            "handlers": ["security_file", "websocket"],
            "level": "INFO",
            "propagate": False,
        },
        "axes": {
            "handlers": ["security_file"],
            "level": "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["celery_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "performance": {
            "handlers": ["performance_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
# ================================================================
# AUDIT CONFIGURATION
# ================================================================
AUDITOR_MIDDLEWARE_ENABLE = True
AUDITOR_MIDDLEWARE_RESTRICT_PATHS = []
AUDITOR_MIDDLEWARE_CONTENT = False

# ================================================================
# DJANGO APPS
# ================================================================
INSTALLED_APPS = [
    # First Third-party apps
    "corsheaders",
    # Django built-in apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "widget_tweaks",
    "django_celery_beat",
    "axes",
    "channels",
    "import_export",
    # Local apps
    "apps.common",
    "apps.account",
    "apps.organizations",
    "apps.inventory",
    "apps.security",
    "apps.audit",
    "apps.billing",
    "apps.pages",
]

# ================================================================
# MIDDLEWARE
# ================================================================
MIDDLEWARE = [
    "apps.audit.middlewares.audit_middleware.AuditMiddleware",
    "apps.audit.view_logging_middleware.ProjectViewLoggingMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "apps.security.middleware.ExponentialBanMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "apps.organizations.middleware.RequireOrganizationMiddleware",
]

# ================================================================
# URLS & WSGI
# ================================================================
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

# ================================================================
# TEMPLATES
# ================================================================
APPS_DIR = BASE_DIR / "apps"

WEB_TEMPLATE_DIRS = [
    app / "web" / "templates"
    for app in APPS_DIR.iterdir()
    if (app / "web" / "templates").exists()
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": WEB_TEMPLATE_DIRS,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.organizations.context_processors.organization_context",
            ],
            "builtins": [
                "apps.common.web.templatetags.currency",
            ],
            "libraries": {
                "assets": "apps.common.web.templatetags.assets",
            }
        },
    },
]

# ================================================================
# DATABASES
# ================================================================

DATABASES = {
    "default": {
        "ENGINE": f"django.db.backends.{os.getenv('DB_ENGINE', 'sqlite3')}",
        "NAME": os.getenv("DB_NAME", "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}

if "test" in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }


# ================================================================
# AUTHENTICATION & PASSWORD VALIDATION
# ================================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_USER_MODEL = "user_account.User"

ACCOUNT_FORMS = {
    "login": "apps.account.forms.CustomLoginForm",
}

LOGIN_URL = "account:login"
LOGIN_REDIRECT_URL = "inventory:home"
LOGOUT_REDIRECT_URL = "account:login"

# ================================================================
# INTERNATIONALIZATION & TIMEZONE
# ================================================================
USE_TZ = True
USE_I18N = True

TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "America/Recife")
LANGUAGE_CODE = os.environ.get("DJANGO_LANGUAGE_CODE", "pt-BR")

LANGUAGES = (
    ("pt-br", "Português"),
    ("en", "English"),
)

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# ================================================================
# STATIC & MEDIA FILES
# ================================================================
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "static/"
STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT", "/usr/share/nginx/html")

STATICFILES_DIRS = [
    p
    for p in (BASE_DIR / "apps").glob("*/web/static")
    if p.is_dir()
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# ================================================================
# CELERY CONFIGURATION
# ================================================================
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONE = "America/Sao_Paulo"
CELERY_TRACK_STARTED = True
CELERY_IGNORE_RESULT = False

# ================================================================
# EMAIL CONFIGURATION
# ================================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

try:
    EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST")
    EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", 465))
    EMAIL_USE_SSL = os.environ.get("DJANGO_EMAIL_USE_SSL", "").lower() in [
        "true", "1", "yes"]
    EMAIL_USE_TLS = os.environ.get("DJANGO_EMAIL_USE_TLS", "").lower() in [
        "true", "1", "yes"]
    EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = os.environ.get(
        "DJANGO_DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

except KeyError as e:
    missing_key = e.args[0]
    raise RuntimeError(
        f"Configuração de e-mail ausente: a variável de ambiente '{missing_key}' não foi definida."
    )

except ValueError as e:
    raise RuntimeError(f"Erro na configuração de e-mail: {e}")

# ================================================================
# MERCADO PAGO
# ================================================================
MERCADO_PAGO_PUBLIC_KEY = os.environ.get("MERCADO_PAGO_PUBLIC_KEY")
MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MERCADO_PAGO_ACCESS_TOKEN")
MERCADO_PAGO_WEBHOOK_SECRET = os.environ.get("MERCADO_PAGO_WEBHOOK_SECRET")


REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# ================================================================
# AXES
# ================================================================
AXES_CACHE = "default"
AXES_EXCLUDE_PATHS = []

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_RESET_ON_SUCCESS = True
AXES_HTTP_RESPONSE_CODE = 429
AXES_LOCKOUT_TEMPLATE = "security/locked.html"


# ================================================================
# CHANNELS
# ================================================================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_URL, 6379)],
        },
    },
}

ALLOWED_WS_ORIGINS = [
    origin for origin in os.environ.get("ALLOWED_WS_ORIGINS", "").split(",") if origin
]


CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
    "accept",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# ================================================================
# STORAGE
# ================================================================

STORAGE_TOKEN = os.environ.get("STORAGE_TOKEN", "")
STORAGE_BASE_URL = os.environ.get("STORAGE_BASE_URL", "")
