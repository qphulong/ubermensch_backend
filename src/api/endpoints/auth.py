from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.schemas import Token
from src.crud.user import get_user
from src.core.security import verify_password
from src.services.auth import create_access_token
from src.api.dependencies import get_db
from src.services.otp import generate_otp
from src.services.email import send_register_otp_email
from src.crud.register_otps import create_otp
from src.crud.user import create_user, get_user_by_email
from src.schemas.schemas import  EmailSchema, UserLogin

router = APIRouter()

@router.post("/login", response_model=Token)
def login(form_data: UserLogin = Depends(), db: Session = Depends(get_db)):
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/send-register-otp")
def send_otp(email_schema: EmailSchema, db: Session = Depends(get_db)):
    email = email_schema.email
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")
    otp = generate_otp()
    create_otp(db, email, otp)
    try:
        send_register_otp_email(email, otp)
        return {"message": "OTP sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send OTP")


