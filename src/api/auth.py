from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.schemas.schemas import UserCreate, UserOut, UserRegister, EmailSchema, UserLogin, PasswordResetSchema
from src.services.otp import create_otp, verify_otp, generate_otp
from src.core.security import verify_password, create_token
from src.dependencies.auth import AccessTokenBearer, RefreshTokenBearer, get_current_user, RoleChecker
from src.db.session import get_db
from src.services.email import send_register_otp_email
from src.services.auth import UserService
from src.core.config import settings
from src.db.redis import add_token_to_blocklist
import datetime

router = APIRouter()
user_service = UserService()
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(allowed_roles=["admin"])

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
                    'password': user.password,
                    'role': user.role
                }
            )

            refresh_token = create_token(
                user_data={
                    'username': user.username,
                    'email': user.gmail_address,
                    'password': user.password,
                    'role': user.role
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

@router.get("/refresh-token")
def get_new_access_token(
    token_details: dict = Depends(refresh_token_bearer),
):
    expiry_timestamp = token_details['exp']
    expiry_date = datetime.datetime.utcfromtimestamp(expiry_timestamp)

    if expiry_date > datetime.datetime.utcnow():
        new_access_token = create_token(
            user_data=token_details['user']
        )
        return JSONResponse(
            content={
                "message": "New access token generated",
                "access_token": new_access_token
            }
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Refresh token expired"
    )

@router.get("/logout")
def logout(token_details: dict = Depends(access_token_bearer)):
    jti = token_details['jti']
    add_token_to_blocklist(jti)
    return JSONResponse(
        content={"message": "Logged out successfully"},
        status_code=status.HTTP_200_OK
    )

@router.post("/reset-password")
def reset_password(
    email_schema: PasswordResetSchema,
    new_password: str,
    otp: str,
    db: Session = Depends(get_db)
):
    pass
    
@router.get("/me", response_model=UserOut)
def read_users_me(user = Depends(get_current_user)):
    return user