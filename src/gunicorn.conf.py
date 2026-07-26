import logging
import os
import threading
import time

DAILY_CHECK_INTERVAL_SECONDS = 24 * 60 * 60
STARTUP_DELAY_SECONDS = 60


def post_fork(server, worker):
    """Substitui o Celery Beat: dispara a checagem periódica de empréstimos
    atrasados, sem precisar de broker, worker ou scheduler externos.

    Roda em post_fork (dentro do processo do worker, depois do fork já ter
    acontecido) e não em when_ready (processo master, antes do fork) — iniciar
    a thread antes do fork trava o worker: ele pode herdar um lock do import
    ou do registro de apps do Django preso no meio de uma operação pela thread
    que não sobrevive ao fork.

    Só faz sentido sem duplicar porque a imagem sobe com um único worker
    (sem --workers na CMD do Dockerfile). Se isso mudar, precisa de um lock
    (ex.: arquivo) pra garantir que só uma réplica rode o loop.
    """
    threading.Thread(target=_run_overdue_loans_scheduler, daemon=True).start()


def _run_overdue_loans_scheduler():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    import django
    django.setup()

    from django.db import close_old_connections

    from apps.inventory.tasks import check_overdue_loans

    logger = logging.getLogger("inventory.tasks")
    time.sleep(STARTUP_DELAY_SECONDS)

    while True:
        try:
            check_overdue_loans()
        except Exception:
            logger.exception("Falha na checagem periódica de empréstimos atrasados")
        finally:
            close_old_connections()
        time.sleep(DAILY_CHECK_INTERVAL_SECONDS)
