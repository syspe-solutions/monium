from pydantic import BaseModel


class DatabaseConfigurationDTO(BaseModel):
    engine: str  # "sqlite3" ou "postgresql" — mesmo vocabulário de DB_ENGINE
    name: str
    user: str = ""
    password: str = ""
    host: str = ""
    port: str = ""
