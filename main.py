from fastapi import FastAPI
from src.core.startup import init_app
from src.api.auth import router as auth_router
from src.api.users import router as users_router
from fastapi.middleware.cors import CORSMiddleware
import yaml

app = FastAPI()

# Load CORS configuration
with open("config.yaml", "r") as config_file:
    cors_config = yaml.safe_load(config_file).get("cors", {})

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.get("allow_origins", []),
    allow_credentials=cors_config.get("allow_credentials", False),
    allow_methods=cors_config.get("allow_methods", ["*"]),
    allow_headers=cors_config.get("allow_headers", ["*"]),
)

# Initialize app with database and scheduler
init_app(app)

# Include routers
app.include_router(auth_router, tags=["auth"])
app.include_router(users_router, tags=["users"])

@app.get("/", response_model=str)
def read_root():
    return "Hallo, übermensch!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)