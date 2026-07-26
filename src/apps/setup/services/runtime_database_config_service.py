import os
import tempfile
from pathlib import Path
from typing import Optional

from django.conf import settings
from dotenv import dotenv_values

from apps.setup.dtos.database_configuration_dto import DatabaseConfigurationDTO

_FIELD_TO_ENV_KEY = {
    "engine": "DB_ENGINE",
    "name": "DB_NAME",
    "user": "DB_USER",
    "password": "DB_PASSWORD",
    "host": "DB_HOST",
    "port": "DB_PORT",
}
_ENV_KEY_TO_FIELD = {value: key for key, value in _FIELD_TO_ENV_KEY.items()}


class RuntimeDatabaseConfigService:
    """Persiste a escolha de banco do instalador em APP_DATA_DIR/database.env —
    um volume Docker que sobrevive à recriação do container — e ativa a escolha
    SQLite imediatamente, sem restart, já que o processo atual já está rodando
    contra o mesmo arquivo SQLite (era o default antes do instalador confirmar)."""

    def persist(self, configuration: DatabaseConfigurationDTO) -> None:
        lines = [
            f"{_FIELD_TO_ENV_KEY[field]}={value}"
            for field, value in configuration.model_dump().items()
            if value != ""
        ]
        self._write_atomically(settings.RUNTIME_DB_CONFIG_PATH, "\n".join(lines) + "\n")

    def apply_without_restart(self) -> None:
        settings.DATABASE_SETUP_REQUIRED = False

    def load_persisted(self) -> Optional[DatabaseConfigurationDTO]:
        """Lê a última escolha salva, se houver — usado pra pré-preencher o
        formulário quando o operador volta pro passo do banco."""
        if not settings.RUNTIME_DB_CONFIG_PATH.exists():
            return None
        values = dotenv_values(settings.RUNTIME_DB_CONFIG_PATH)
        fields = {
            _ENV_KEY_TO_FIELD[key]: value
            for key, value in values.items()
            if key in _ENV_KEY_TO_FIELD and value is not None
        }
        if "engine" not in fields:
            return None
        return DatabaseConfigurationDTO(**fields)

    def _write_atomically(self, destination: Path, content: str) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        file_descriptor, temp_path = tempfile.mkstemp(dir=destination.parent)
        with os.fdopen(file_descriptor, "w") as temp_file:
            temp_file.write(content)
        os.replace(temp_path, destination)
