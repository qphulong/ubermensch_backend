from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.user import UserCreate
from src.core.security import get_password_hash

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate, role: str = "normal"):
    db_user = User(
        username=user.username,
        password=get_password_hash(user.password),
        git_profile_link=user.git_profile_link,
        gmail_address=user.gmail_address,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user