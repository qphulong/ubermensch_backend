from fastapi import FastAPI
from sqlalchemy.orm import Session
from src.db.session import Base, engine, SessionLocal
from src.schemas.schemas import UserCreate
from src.services.auth import UserService
from src.models.user import User
from src.models.register_otps import RegisterOTPs
from src.core.config import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.services.otps_cleanup import cleanup_expired_otps
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
user_service = UserService()

def init_db():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        admins = db.query(User).filter(User.role == "admin").all()
        if not admins:
            admin_user = UserCreate(
                username=settings.ADMIN_USERNAME,
                password=settings.ADMIN_PASSWORD,
                git_profile_link=settings.ADMIN_GIT_LINK,
                gmail_address=settings.ADMIN_EMAIL
            )
            user_service.create_user(db, admin_user, role="admin")
            logger.info(f"Admin user created with username '{settings.ADMIN_USERNAME}'")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
    finally:
        db.close()

def setup_scheduler():
    scheduler.add_job(cleanup_expired_otps, "interval", minutes=settings.OTP_CLEANUP_INTERVAL)
    scheduler.start()
    # logger.info("Scheduler started for OTP cleanup every 5 minutes")

def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler shut down")

def init_app(app: FastAPI):
    init_db()
    app.add_event_handler("startup", setup_scheduler)
    app.add_event_handler("shutdown", shutdown_scheduler)