import os
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from .database import SessionLocal
from .models import User
from .schemas import UserCreate, UserOut, Token, UserLogin
from .schemas import UserCreate, UserOut, Token, UserLogin, ForgetPasswordRequest, ChangePasswordRequest
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set in environment variables")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#region Authentication
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
#endregion

#region User CRUD
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate, role: str = "normal"):
    db_user = User(
        username=user.username,
        password=get_password_hash(user.password),
        git_profile_link=user.git_profile_link,
        gmail_address=user.gmail_address,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user: User, new_password: str):
    user.password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user
#endregion

#region User APIs
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED ,response_model=UserOut)
async def register(user: UserCreate, db: db_dependency):
    existing = get_user(db, user.username)
    if existing:
        raise HTTPException(status_code=401, detail="User already exists")
    return create_user(db, user)

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: db_dependency):
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/forget-password")
def forget_password(data: ForgetPasswordRequest, db: db_dependency):
    user = get_user(db, data.username)
    if not user:
        raise HTTPException(status_code=404, detail="Username not found")
    update_user_password(db, user, data.new_password)
    return {"msg": "Password reset successful"}

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(status_code=401, detail="Incorrect old password")
    update_user_password(db, current_user, data.new_password)
    return {"msg": "Password changed successfully"}

#endregion

