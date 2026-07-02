from pydantic import BaseModel, EmailStr


class CreateUserDTO(BaseModel):
    username: str
    password: str
    email: EmailStr
