from pydantic import BaseModel


class LoginUserDTO(BaseModel):
    username: str
    password: str


