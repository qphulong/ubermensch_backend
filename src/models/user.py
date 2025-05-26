<<<<<<< HEAD:app/models.py
from sqlalchemy import Column, String, Enum, BigInteger
from .database import Base
=======
from sqlalchemy import Column, String, Enum
from src.db.session import Base
>>>>>>> origin/develop:src/models/user.py
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
<<<<<<< HEAD:app/models.py
    role = Column(Enum(RoleEnum), nullable=False)
    last_accessed = Column(BigInteger, nullable=True, default=None)
    session_start = Column(BigInteger, nullable=True, default=None)
    password_reset_expiry = Column(BigInteger, nullable=True, default=None)

=======
    role = Column(Enum(RoleEnum), nullable=False)
>>>>>>> origin/develop:src/models/user.py
