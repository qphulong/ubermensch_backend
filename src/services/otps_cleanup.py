from sqlalchemy.orm import Session
from src.crud.register_otps import delete_expired_otps
from src.db.session import get_db
import logging

logger = logging.getLogger(__name__)

def cleanup_expired_otps():
    db: Session = next(get_db())
    try:
        deleted_count = delete_expired_otps(db)
        logger.info(f"Cleanup completed: {deleted_count} expired OTPs deleted")
    except Exception as e:
        logger.error(f"Error during OTP cleanup: {str(e)}")
    finally:
        db.close()