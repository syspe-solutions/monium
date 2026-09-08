import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

# Context variables for request-level metadata
_request_context: ContextVar[Dict[str, Any]] = ContextVar("request_context", default={})

def set_request_context(
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    trace_id: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
) -> None:
    context = {
        "user_id": user_id,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "trace_id": trace_id or str(uuid.uuid4()),
        "path": path,
        "method": method,
    }
    _request_context.set(context)

def get_request_context() -> Dict[str, Any]:
    return _request_context.get()

def clear_request_context() -> None:
    _request_context.set({})

def get_trace_id() -> str:
    return _request_context.get().get("trace_id", "no-trace-id")
