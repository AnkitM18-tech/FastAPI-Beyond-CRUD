from fastapi import FastAPI
from fastapi.requests import Request
import time
import logging

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed in {process_time} seconds"
        print(message)
        return response
    
    @app.middleware("http")
    async def authorization(request: Request, call_next):
        pass