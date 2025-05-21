import random
from datetime import datetime
from sqlalchemy.orm import Session
from src.crud.register_otps import get_otp_by_email

def generate_otp():
    return str(random.randint(100000, 999999))

def verify_otp(db: Session, email: str, otp: str):
    db_otp = get_otp_by_email(db, email)
    if db_otp and db_otp.otp == otp and db_otp.expired_at > datetime.now():
        return True
    return False