from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.db.main import init_db
from .errors import create_exception_handler, InvalidCredentials, InvalidToken, RevokedToken, BookNotFound, UserNotFound, ReviewNotFound, InsufficientPermission, UserAlreadyExists, AccessTokenRequired, RefreshTokenRequired

@asynccontextmanager
async def life_span(app: FastAPI):
    print("=============================== Server is starting ================================== ")
    await init_db()
    yield 
    print("=============================== Server has been stopped ============================= ")

version = "v1"

app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version=version,
)

app.add_exception_handler(
    UserAlreadyExists,
    create_exception_handler(status_code=status.HTTP_409_CONFLICT, initial_detail={"message": "User already exists", "error_code": "USER_ALREADY_EXISTS"})
)
app.add_exception_handler(
    InvalidCredentials,
    create_exception_handler(status_code=status.HTTP_400_BAD_REQUEST, initial_detail={"message": "Invalid email or password", "error_code": "INVALID_CREDENTIALS"})
)
app.add_exception_handler(
    InvalidToken,
    create_exception_handler(status_code=status.HTTP_401_UNAUTHORIZED, initial_detail={"message": "Token is invalid or expired", "error_code": "INVALID_TOKEN", "resolution": "Please get a new token"})
)
app.add_exception_handler(
    RevokedToken,
    create_exception_handler(status_code=status.HTTP_401_UNAUTHORIZED, initial_detail={"message": "Token is invalid or has been revoked", "error_code": "REVOKED_TOKEN", "resolution": "Please get a new token"})
)
app.add_exception_handler(
    BookNotFound,
    create_exception_handler(status_code=status.HTTP_404_NOT_FOUND, initial_detail={"message": "Book Not Found", "error_code": "BOOK_NOT_FOUND"})
)
app.add_exception_handler(
    UserNotFound,
    create_exception_handler(status_code=status.HTTP_404_NOT_FOUND, initial_detail={"message": "User Not Found", "error_code": "USER_NOT_FOUND"})
)
app.add_exception_handler(
    ReviewNotFound,
    create_exception_handler(status_code=status.HTTP_404_NOT_FOUND, initial_detail={"message": "Review Not Found", "error_code": "REVIEW_NOT_FOUND"})
)
app.add_exception_handler(
    InsufficientPermission,
    create_exception_handler(status_code=status.HTTP_403_FORBIDDEN, initial_detail={"message": "User does not have required permissions to perform this action", "error_code": "INSUFFICIENT_PERMISSION"})
)
app.add_exception_handler(
    AccessTokenRequired,
    create_exception_handler(status_code=status.HTTP_401_UNAUTHORIZED, initial_detail={"message": "Please provide a valid Access Token", "error_code": "ACCESS_TOKEN_REQUIRED", "resolution": "Please get a new access token"})
)
app.add_exception_handler(
    RefreshTokenRequired,
    create_exception_handler(status_code=status.HTTP_403_FORBIDDEN, initial_detail={"message": "Please provide a valid Refresh Token", "error_code": "REFRESH_TOKEN_REQUIRED", "resolution": "Please get a new refresh token"})
)

@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(
        content={"message": "Internal Server Error - Something went wrong", "error_code": "INTERNAL_SERVER_ERROR"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])