from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
from src.core.config import settings
from src.models.user import User
from sqlalchemy.orm import Session
from src.schemas.schemas import UserCreate
from src.core.security import get_password_hash

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
    
class UserService:
    def get_user_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.gmail_address == email).first()
    
    def email_exists(self, db: Session, email: str):      
        user = self.get_user_by_email(db, email)
        return user is not None
    
    def get_user_by_username(self, db: Session, username: str):
        return db.query(User).filter(User.username == username).first()
    
    def username_exists(self, db: Session, username: str):
        user = self.get_user_by_username(db, username)
        return user is not None
    
    def create_user(self, db: Session, user: UserCreate, role: str = "normal"):
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