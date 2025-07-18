from fastapi import FastAPI
from src.core.startup import init_app
from src.api.auth import router as auth_router
from src.api.search_engine import router as search_engine_router
from fastapi.middleware.cors import CORSMiddleware
from src.middleware import register_middleware
import yaml

version = "0.1.0"

app = FastAPI(
    title="Übermensch API",
    description="API for Übermensch project",
    version=version,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Übermensch Team",
        "email": "selenajexin458@gmail.com"
    }
)

# Load CORS configuration
with open("config.yaml", "r") as config_file:
    cors_config = yaml.safe_load(config_file).get("cors", {})

register_middleware(app, cors_config=cors_config)

# Initialize app with database and scheduler
init_app(app)

# Include routers
app.include_router(auth_router, tags=["auth"])
app.include_router(search_engine_router)

@app.get("/", response_model=str)
def read_root():
    return "Hallo, übermensch!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)