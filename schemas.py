from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str  # Hashed password from frontend
    role: str = "normal_user"

class UserLogin(BaseModel):
    username: str
    password: str  # Hashed password from frontend

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    username: str
    role: str