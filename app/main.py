from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from .database import Base, engine, SessionLocal
from .schemas import UserCreate, UserOut
from .models import User
from .auth import create_user, verify_token, get_user, get_current_user
from . import auth
from typing import Annotated

import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "defaultpassword")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_GIT_LINK = os.getenv("ADMIN_GIT_LINK", "")

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db: Session = SessionLocal()
    try:
        admins = db.query(User).filter(User.role == "admin").all()
        if not admins:
            admin_user = UserCreate(
                username=ADMIN_USERNAME,
                password=ADMIN_PASSWORD,
                git_profile_link=ADMIN_GIT_LINK,
                gmail_address=ADMIN_EMAIL
            )
            create_user(db, admin_user, role="admin")
            print(f"Admin user created with username '{ADMIN_USERNAME}' and password '{ADMIN_PASSWORD}'. Please change the password.")
        yield
    finally:
        db.close()

app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/",response_model=str)
def read_root():
    return "Hallo, übermensch!"

@app.get("/me", response_model=UserOut)
def read_users_me(token: str, db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user(db, payload["sub"])
    return user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)