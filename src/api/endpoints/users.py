from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.user import UserCreate, UserOut
from src.crud.user import create_user, get_user
from src.api.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = get_user(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    return create_user(db, user)

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return current_user