from pydantic import BaseModel
from enum import Enum

class RoleEnum(str, Enum):
    normal = "normal"
    manager = "manager"
    admin = "admin"

class UserCreate(BaseModel):
    username: str
    password: str
    git_profile_link: str
    gmail_address: str

class UserRegister(UserCreate):
    otp: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str
    git_profile_link: str
    gmail_address: str
    role: RoleEnum

    class Config:
        from_attributes = True

class EmailSchema(BaseModel):
    email: str

class PasswordResetRequestSchema(BaseModel):
    email: str

class PasswordResetSchema(BaseModel):
    email: str
    new_password: str
    new_password_repeat: str
    otp: str