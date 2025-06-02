from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.schemas import Token, UserCreate, UserOut, UserRegister
from src.services.otp import verify_otp
from src.services.auth import verify_token
from src.core.security import verify_password
from src.services.auth import create_access_token
from src.db.session import get_db
from src.services.otp import generate_otp
from src.services.email import send_register_otp_email
from src.crud.register_otps import create_otp
from src.schemas.schemas import EmailSchema, UserLogin
from src.services.auth import UserService

router = APIRouter()
user_service = UserService()

@router.post("/login", response_model=Token)
def login(form_data: UserLogin = Depends(), db: Session = Depends(get_db)):
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/send-register-otp")
def send_register_otp(email_schema: EmailSchema, db: Session = Depends(get_db)):
    email = email_schema.email
    if user_service.email_exists(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")
    otp = generate_otp()
    create_otp(db, email, otp)
    try:
        send_register_otp_email(email, otp)
        return {"message": "OTP sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

@router.post("/register")
def register(user_register: UserRegister, db: Session = Depends(get_db)):
    if not verify_otp(db, user_register.gmail_address, user_register.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    if user_service.user_exists(user_register.gmail_address, db):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_create = UserCreate(**user_register.model_dump(exclude={"otp"}))
    user_service.create_user(db, user_create)
    return {"message": "User registered successfully"}
    
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