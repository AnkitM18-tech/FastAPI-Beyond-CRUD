from fastapi import Request, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
# from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from .utils import verify_access_token
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from .service import UserService
from src.db.models import User
from src.errors import InvalidToken,AccessTokenRequired, RefreshTokenRequired,InsufficientPermission

user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials = await super().__call__(request)
        token = credentials.credentials

        token_data = verify_access_token(token)

        if not self.verify_token(token):
            raise InvalidToken()
        
        if await token_in_blocklist(token_data["jti"]):
            raise InvalidToken()

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
            raise AccessTokenRequired()

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()

async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    user_email = token_details["user"]["email"]
    user = await user_service.get_user_by_email(user_email, session)

    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User= Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise InsufficientPermission()
        return True