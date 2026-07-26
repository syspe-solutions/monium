from pydantic import BaseModel


class EmailConfigurationDTO(BaseModel):
    host: str
    port: int
    use_tls: bool = False
    use_ssl: bool = False
    username: str = ""
    password: str = ""
    default_from_email: str
