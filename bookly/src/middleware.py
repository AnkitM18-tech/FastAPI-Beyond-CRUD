from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
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
    
    # @app.middleware("http")
    # async def authorization(request: Request, call_next):
    #     if "Authorization" not in request.headers:
    #         return JSONResponse(status_code=401, content={"message": "Missing Authorization Header", "resolution": "Please provide the right credentials to proceed"})
    #     return await call_next(request)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"],
    )