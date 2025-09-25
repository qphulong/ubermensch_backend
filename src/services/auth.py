from src.models.user import User
from sqlalchemy.orm import Session
from src.schemas.users import UserCreate
from src.core.security import get_password_hash
    
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
    
    def update_user(self, db: Session, user: User, user_data: dict):
        for key, value in user_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user