from pydantic import BaseModel, Field
from enum import Enum
from typing import List

# TODO: refactor laij casi structure cuar directory schemas
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

# SEARCH ENGINE
class PageRegisterInput(BaseModel):
    id: str
    author: str
    local_url: str
    text: str

class PageRegisterResponse(BaseModel):
    id: str
    success: bool

class SearchQuery(BaseModel):
    query: str
    top_k: int = Field(8, gt=0)

class SearchResult(BaseModel):
    id: str
    author: str
    local_url: str
    distance: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    
class PageUnregister(BaseModel):
    id: str
class PageUnregisterResponse(BaseModel):
    id: str
    author: str
    local_url: str
    success: bool