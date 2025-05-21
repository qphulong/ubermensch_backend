from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.services.auth import verify_token
from src.crud.user import get_user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
