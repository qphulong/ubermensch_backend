from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.register_otps import RegisterOTPs
from src.core.config import settings
from sqlalchemy import delete

def create_otp(db: Session, email: str, otp: str):
    # Remove any existing OTP for this email to ensure only one active OTP
    db.query(RegisterOTPs).filter(RegisterOTPs.email == email).delete()
    expired_at = datetime.now() + timedelta(minutes=settings.OTP_EXPIRED_TIME)
    db_otp = RegisterOTPs(email=email, otp=otp, expired_at=expired_at)
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)
    return db_otp

def get_otp_by_email(db: Session, email: str):
    return db.query(RegisterOTPs).filter(RegisterOTPs.email == email).first()

def delete_expired_otps(db: Session) -> int:
    result = db.execute(
        delete(RegisterOTPs).where(RegisterOTPs.expired_at < datetime.now())
    )
    db.commit()
    return result.rowcount