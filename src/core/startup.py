from sqlalchemy.orm import Session
from src.db.session import Base, engine, SessionLocal
from src.schemas.user import UserCreate
from src.crud.user import create_user
from src.models.user import User
from src.core.config import settings

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
            create_user(db, admin_user, role="admin")
            print(f"Admin user created with username '{settings.ADMIN_USERNAME}' and password '{settings.ADMIN_PASSWORD}'. Please change the password.")
    finally:
        db.close()