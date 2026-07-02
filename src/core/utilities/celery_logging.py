import logging
from celery.signals import task_prerun, task_postrun, task_failure
from core.utilities.logging_context import set_request_context, clear_request_context

logger = logging.getLogger("celery.task")

@task_prerun.connect
def on_task_prerun(task_id, task, *args, **kwargs):
    """Set up context before task runs."""
    # Celery tasks might have been triggered with a trace_id in kwargs
    trace_id = kwargs.get('trace_id')
    user_id = kwargs.get('user_id')
    
    set_request_context(
        user_id=user_id,
        trace_id=trace_id,
        path=f"celery://{task.name}",
        method="TASK"
    )
    logger.info(f"Task {task.name}[{task_id}] started", extra={
        "extra_data": {
            "task_name": task.name,
            "task_id": task_id,
            "args": str(args),
            "kwargs": str(kwargs),
            "event": "task_started"
        }
    })

@task_postrun.connect
def on_task_postrun(task_id, task, retval, state, *args, **kwargs):
    """Clean up context after task runs."""
    logger.info(f"Task {task.name}[{task_id}] finished with state {state}", extra={
        "extra_data": {
            "task_name": task.name,
            "task_id": task_id,
            "state": state,
            "event": "task_finished"
        }
    })
    clear_request_context()

@task_failure.connect
def on_task_failure(task_id, exception, args, kwargs, traceback, einfo, **extra):
    """Log task failure with details."""
    logger.error(f"Task failed: {task_id}", exc_info=exception, extra={
        "extra_data": {
            "task_id": task_id,
            "exception": str(exception),
            "event": "task_failed"
        }
    })
