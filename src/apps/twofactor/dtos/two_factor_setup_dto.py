from pydantic import BaseModel


class TwoFactorSetupDTO(BaseModel):
    masked_email: str
