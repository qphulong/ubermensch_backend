from sqlalchemy import Column, String, Enum, BigInteger
from .database import Base
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

    lastAccessed = Column(BigInteger, nullable=True, default=None)
    sessionStart = Column(BigInteger, nullable=True, default=None)
    passwordResetExpiry = Column(BigInteger, nullable=True, default=None)

