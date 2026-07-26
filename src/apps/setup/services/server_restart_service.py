import os
import threading
import time

RESTART_DELAY_SECONDS = 1.5


class ServerRestartService:
    """Depois que uma configuração de banco externo é persistida, o processo
    atual precisa reiniciar pra reimportar core.settings com o DATABASES novo —
    trocar a conexão em tempo real é frágil demais pra confiar num fluxo crítico
    como esse. Encerra o processo alguns segundos depois da resposta ser
    enviada; a política `restart: always` do compose sobe o container de novo,
    já rodando `migrate` contra o banco escolhido antes do gunicorn subir."""

    def schedule_restart(self) -> None:
        threading.Thread(target=self._restart_after_delay, daemon=True).start()

    def _restart_after_delay(self) -> None:
        time.sleep(RESTART_DELAY_SECONDS)
        os._exit(0)
