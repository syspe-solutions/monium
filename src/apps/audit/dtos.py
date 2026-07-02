from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict


@dataclass
class LayerState:
    total: int
    levels: Dict[str, int]
    rpm_buckets: Dict[str, int]
    file_offset: int
    file_inode: int
    file_size: int


class SecurityStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    SUSPICIOUS = "suspicious"
    CRITICAL = "critical" 


class SecurityAction(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"

    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_CONFIRM = "password_reset_confirm"

    MFA_CODE_SENT = "mfa_code_sent"
    MFA_VERIFIED = "mfa_verified"
    MFA_FAILED = "mfa_failed"

    ACCOUNT_LOCKOUT = "account_lockout"
    ACCOUNT_UNLOCKED = "account_unlocked"
    SESSION_EXPIRED = "session_expired"
    SESSION_HIJACK_ATTEMPT = "session_hijack_detected"

    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_CHANGE = "permission_change"

    SENSITIVE_DATA_ACCESS = "sensitive_data_access" 
    EXPORT_STARTED = "export_started"


class BusinessAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    PROCESS = "process"
    APPROVE = "approve"
    REJECT = "reject"
    SUBMIT = "submit"
    CANCEL = "cancel"
    DOWNLOAD = "download"
    UPLOAD = "upload"


class ErrorType(str, Enum):
    HTTP_SERVER_ERROR = "http_server_error"
    HTTP_CLIENT_ERROR = "http_client_error"
    DATABASE_ERROR = "database_error"
    EXTERNAL_API_ERROR = "external_api_error"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    FILE_SYSTEM_ERROR = "file_system_error"
    CELERY_TASK_ERROR = "celery_task_error"
    UNKNOWN_ERROR = "unknown_error"


class PerformanceAction(str, Enum):
    REQUEST_TIME = "request_time"
    DB_QUERY_TIME = "db_query_time"
    EXTERNAL_API_TIME = "external_api_time"
    CELERY_TASK_TIME = "celery_task_time"
    CACHE_HIT_TIME = "cache_hit_time"
    CACHE_MISS_TIME = "cache_miss_time"


class DatabaseAction(str, Enum):
    QUERY = "query"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    TRANSACTION_START = "transaction_start"
    TRANSACTION_COMMIT = "transaction_commit"
    TRANSACTION_ROLLBACK = "transaction_rollback"
    MIGRATION = "migration"