import logging
from typing import Optional

import requests
from django.conf import settings

from apps.common.models import StoredFile

logger = logging.getLogger(__name__)

PRIVATE_FOLDER_TYPES = {"documents", "profile", "attachments"}
PUBLIC_FOLDER_TYPES = {"media"}
HEALTH_TIMEOUT = 10.0


class FileStoreService:
    def __init__(self):
        self.base_url = settings.STORAGE_BASE_URL
        self.token = settings.STORAGE_TOKEN

    def upload(
        self,
        file_obj,
        folder_type: str,
        owner_id: Optional[str] = None,
    ) -> Optional[StoredFile]:
        is_private = owner_id is not None

        if is_private and folder_type not in PRIVATE_FOLDER_TYPES:
            raise ValueError(
                f"Tipo de pasta inválido para upload privado: '{folder_type}'. "
                f"Valores permitidos: {sorted(PRIVATE_FOLDER_TYPES)}"
            )

        if not is_private and folder_type not in PUBLIC_FOLDER_TYPES:
            raise ValueError(
                f"Tipo de pasta inválido para upload público: '{folder_type}'. "
                f"Valores permitidos: {sorted(PUBLIC_FOLDER_TYPES)}"
            )

        headers = {
            "X-Storage-Token": self.token,
            "X-Folder-Type": folder_type,
        }
        if owner_id is not None:
            headers["X-Owner-ID"] = str(owner_id)

        files = {"file": (file_obj.name, file_obj.read(), file_obj.content_type)}

        try:
            response = requests.post(
                f"{self.base_url}/storage/upload",
                headers=headers,
                files=files,
                timeout=30.0,
            )

            if response.status_code == 201:
                relative_path = response.json()["data"]["relative_path"]
                stored_file, _ = StoredFile.objects.get_or_create(relative_path=relative_path)
                return stored_file

            logger.error("Storage upload error: %s - %s", response.status_code, response.text)
            return None

        except requests.RequestException as e:
            logger.error("Storage connection error: %s", e)
            return None

    def health_check(self) -> dict:
        headers = {"X-Storage-Token": self.token}
        response = requests.get(
            f"{self.base_url}/health",
            headers=headers,
            timeout=HEALTH_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        return {
            "status": payload.get("status", "unknown"),
            "storage_capacity": payload.get("storage_capacity", "unknown"),
        }

    def get_file(self, relative_path: str) -> Optional[requests.Response]:
        headers = {"X-Storage-Token": self.token}

        try:
            response = requests.get(
                f"{self.base_url}/storage/file/{relative_path}",
                headers=headers,
                timeout=30.0,
                stream=True,
            )

            if response.status_code == 200:
                return response

            return None

        except requests.RequestException as e:
            logger.error("Storage get_file error: %s", e)
            return None
