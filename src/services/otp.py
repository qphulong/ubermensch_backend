from sqlalchemy import delete
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from src.models.register_otps import RegisterOTPs
from src.db.session import get_db
from src.core.config import settings
import random
import logging

logger = logging.getLogger(__name__)

def generate_otp():
    return str(random.randint(100000, 999999))

def verify_otp(db: Session, email: str, otp: str):
    db_otp = get_otp_by_email(db, email)
    if db_otp and db_otp.otp == otp and db_otp.expired_at > datetime.now():
        return True
    return False

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

def cleanup_expired_otps():
    db: Session = next(get_db())
    try:
        deleted_count = delete_expired_otps(db)
        logger.info(f"Cleanup completed: {deleted_count} expired OTPs deleted")
    except Exception as e:
        logger.error(f"Error during OTP cleanup: {str(e)}")
    finally:
        db.close()