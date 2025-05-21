from sqlalchemy import Column, String, Enum
from src.db.session import Base
import enum

class RoleEnum(str, enum.Enum):
    normal = "normal"
    manager = "manager"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)
    git_profile_link = Column(String)
    gmail_address = Column(String)
    role = Column(Enum(RoleEnum), nullable=False)