from fastapi import FastAPI, Request
import time
import logging

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

def register_middleware(app: FastAPI, cors_config: dict = None):
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)
        processing_time = time.time() - start_time

        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time:.4f}s"

        print(message)

        return response
    
    if cors_config:
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_config.get("allow_origins", []),
            allow_credentials=cors_config.get("allow_credentials", False),
            allow_methods=cors_config.get("allow_methods", ["*"]),
            allow_headers=cors_config.get("allow_headers", ["*"]),
        )
