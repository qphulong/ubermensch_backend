from sqlalchemy import Column, String, ForeignKey
from pgvector.sqlalchemy import Vector
from src.db.session import Base

class PagesIndex(Base):
    __tablename__ = "pages_index"
    
    id = Column(String, primary_key=True, index=True)
    author = Column(String, ForeignKey("users.username"), nullable=False)
    local_url = Column(String, nullable=False)
    embedding_vector = Column(Vector(1536), nullable=True)