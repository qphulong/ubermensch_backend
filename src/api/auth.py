from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.schemas.schemas import Token, UserCreate, UserOut, UserRegister, EmailSchema, UserLogin
from src.services.otp import verify_otp, generate_otp
from src.core.security import verify_password, create_token, verify_token, decode_token
from src.db.session import get_db
from src.services.email import send_register_otp_email
from src.crud.register_otps import create_otp
from src.services.auth import UserService

router = APIRouter()
user_service = UserService()

@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    username = login_data.username
    password = login_data.password

    user = user_service.get_user_by_username(db, username)
    if user is not None:
        password_verified = verify_password(password, user.password)
        if password_verified:
            access_token = create_token(
                user_data={
                    'username': user.username,
                    'email': user.gmail_address,
                    'password': user.password
                }
            )

            refresh_token = create_token(
                user_data={
                    'username': user.username,
                    'email': user.gmail_address,
                    'password': user.password
                },
                refresh=True
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "username": user.username,
                        "email": user.gmail_address,
                        "role": user.role
                    }
                }
            )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username")

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
    
    if user_service.email_exists(db, user_register.gmail_address):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if user_service.username_exists(db, user_register.username):
        raise HTTPException(status_code=400, detail="Username already taken")

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
    user = user_service.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user