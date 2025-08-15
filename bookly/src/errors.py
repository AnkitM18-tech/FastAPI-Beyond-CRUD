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