from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.schemas import UserCreate, UserOut
from src.crud.user import create_user
from src.db.session import get_db
from src.crud.user import create_user, get_user_by_email
from src.schemas.schemas import UserCreate, UserRegister
from src.services.otp import verify_otp
from src.services.auth import verify_token
from src.crud.user import get_user

router = APIRouter()

@router.get("/me", response_model=UserOut)
def read_users_me(token: str, db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register")
def register(user_register: UserRegister, db: Session = Depends(get_db)):
    if not verify_otp(db, user_register.gmail_address, user_register.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    if get_user_by_email(db, user_register.gmail_address):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_create = UserCreate(**user_register.model_dump(exclude={"otp"}))
    create_user(db, user_create)
    return {"message": "User registered successfully"}