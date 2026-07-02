import celery
from core.utilities.logging_context import get_request_context

class TraceableTask(celery.Task):
    """
    Base Celery Task that automatically propagates trace_id and user_id 
    from request context to task headers.
    """
    def apply_async(self, args=None, kwargs=None, **options):
        context = get_request_context()
        
        # Inject context into headers for propagation
        headers = options.setdefault("headers", {})
        headers.update({
            "trace_id": context.get("trace_id"),
            "user_id": context.get("user_id"),
        })
        
        return super().apply_async(args, kwargs, **options)
