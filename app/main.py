from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from .database import Base, engine, SessionLocal
from .schemas import UserCreate, UserOut, Token, UserLogin
from .crud import create_user, get_user
from .auth import verify_password, create_access_token, verify_token
from .models import User
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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/",response_model=str)
def read_root():
    return "Hallo, übermensch!"

@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = get_user(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    return create_user(db, user)

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user(db, user.username)
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

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