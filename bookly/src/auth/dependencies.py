from fastapi import Request, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException

from .utils import verify_access_token
from src.db.redis import token_in_blocklist

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials = await super().__call__(request)
        token = credentials.credentials

        token_data = verify_access_token(token)

        if not self.verify_token(token):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                "error": "Invalid or expired token",
                "resolution": "Please get a new token"
            })
        
        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                "error": "Token is invalid or has been revoked",
                "resolution": "Please get a new token"
            })

        self.verify_token_data(token_data)

        return token_data
    
    def verify_token(self, token: str) -> bool:
        token_data = verify_access_token(token)
        return True if token_data is not None else False
    
    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Please Override this method in child classes")
    
class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please provide an access token")

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please provide a refresh token")