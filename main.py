from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User
from schemas import UserCreate, UserLogin, Token, UserOut
from auth import create_access_token, verify_token

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5173",  # Allow localhost during development
    "https://ubermensch-frontend.onrender.com",  # Add your deployed frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Existing endpoints
@app.get("/")
def read_root():
    return {"message": "Hallo, ubermensch!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# New endpoints for authentication and RBAC
@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Store the hashed password directly (hashed in frontend)
    db_user = User(username=user.username, hashed_password=user.password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"username": db_user.username, "role": db_user.role}

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or db_user.hashed_password != user.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.username, "role": db_user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected/admin", response_model=UserOut)
def admin_route(token: str = Depends(oauth2_scheme)):
    credentials = verify_token(token)
    if credentials["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return credentials

@app.get("/protected/manager", response_model=UserOut)
def manager_route(token: str = Depends(oauth2_scheme)):
    credentials = verify_token(token)
    if credentials["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Manager or Admin access required")
    return credentials

@app.get("/protected/user", response_model=UserOut)
def user_route(token: str = Depends(oauth2_scheme)):
    credentials = verify_token(token)
    return credentials

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)