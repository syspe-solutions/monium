from typing import Optional

from pydantic import BaseModel


class LoginResultDTO(BaseModel):
    success: bool
    user: Optional[object] = None
    error_code: Optional[str] = None
