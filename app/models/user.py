from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str
    email: EmailStr
