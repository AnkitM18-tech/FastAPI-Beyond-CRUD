from fastapi import status, FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from typing import Any, Callable


class BooklyException(Exception):
    """
    This is the base class for all bookly exceptions
    """
    pass

class InvalidToken(BooklyException):
    """
    User has provided invalid token or expired token
    """
    pass

class InvalidCredentials(BooklyException):
    """
    User has provided invalid credentials
    """
    pass

class RevokedToken(BooklyException):
    """
    User has provided a token that has been revoked
    """
    pass

class AccessTokenRequired(BooklyException):
    """
    User has provided a refresh token when an access token is needed
    """
    pass

class RefreshTokenRequired(BooklyException):
    """
    User has provided an access token when a refresh token is needed
    """
    pass

class UserAlreadyExists(BooklyException):
    """
    User has provided an email that already exists
    """
    pass

class InsufficientPermission(BooklyException):
    """
    User doesn't have the necessary permissions to perform this action
    """
    pass

class BookNotFound(BooklyException):
    """
    Book Not Found
    """
    pass

class UserNotFound(BooklyException):
    """
    User Not Found
    """
    pass

class ReviewNotFound(BooklyException):
    """
    Review Not Found
    """
    pass

def create_exception_handler(status_code: int, initial_detail: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exception: BooklyException) -> JSONResponse:
        return JSONResponse(status_code=status_code, content=initial_detail)

    return exception_handler

def register_all_errors(app: FastAPI):
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