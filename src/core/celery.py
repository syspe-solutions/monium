from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from str2bool import str2bool

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

DEBUG = str2bool(os.environ.get('DJANGO_DEBUG', False))

# Use our custom TraceableTask by default
from core.utilities.celery_base import TraceableTask

app = Celery("core", task_cls=TraceableTask)

if DEBUG:
    app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        broker_url='memory://',
        result_backend='cache+memory://',
        broker_connection_retry_on_startup=False,
        broker_connection_retry=False,
    )
else:
    app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# Signal registration for context extraction
from celery.signals import task_prerun, task_postrun
from core.utilities.logging_context import set_request_context, clear_request_context

@task_prerun.connect
def on_task_prerun(task, task_id, args, kwargs, **kwargs_extra):
    """Extract context from headers injected by TraceableTask."""
    request_stack = task.request_stack
    current_request = request_stack.top
    
    # Celery headers are usually in current_request.headers
    headers = getattr(current_request, 'headers', {})
    
    set_request_context(
        trace_id=headers.get("trace_id"),
        user_id=headers.get("user_id"),
        path=f"celery://{task.name}",
        method="TASK"
    )

@task_postrun.connect
def on_task_postrun(*args, **kwargs):
    clear_request_context()
