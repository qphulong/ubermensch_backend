from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.core.startup import init_db
from src.api.endpoints.auth import router as auth_router
from src.api.endpoints.users import router as users_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, tags=["auth"])
app.include_router(users_router, tags=["users"])

@app.get("/", response_model=str)
def read_root():
    return "Hallo, übermensch!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)