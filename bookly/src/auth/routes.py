from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta, datetime
from .schemas import CreateUser, UserModel, UserLogin, UserBooks, Email
from .service import UserService
from .utils import create_access_token, verify_password
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.errors import UserAlreadyExists, InvalidCredentials, InvalidToken
from src.mail import mail, create_message

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])
REFRESH_TOKEN_EXPIRY = 2

@auth_router.post("/send_mail")
async def send_mail(emails: Email, session: AsyncSession = Depends(get_session)):
    emails = emails.email_addresses
    html = "<h1>Welcome to the App!</h1>"
    message = create_message(emails, "Welcome", html)

    await mail.send_message(message)

    return {"message": "Email sent successfully"}

@auth_router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: CreateUser, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)
    return new_user

@auth_router.post("/login")
async def login_user(user_data: UserLogin, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    password = user_data.password
    user = await user_service.get_user_by_email(email, session)

    if user is None:
        raise InvalidCredentials()

    if not verify_password(password, user.password):
        raise InvalidCredentials()

    access_token = create_access_token({"email": user.email, "user_uid": str(user.uid), "role": user.role})
    refresh_token = create_access_token({"email": user.email, "user_uid": str(user.uid)}, refresh=True, expiry=timedelta(days= REFRESH_TOKEN_EXPIRY))

    return JSONResponse(
        content={
            "message": "Login Successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "email": user.email,
                "uid": str(user.uid),
                "role": user.role
            }
        }
    )

@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data=token_details["user"]
        )

        return JSONResponse(
            content= {
                "access_token": new_access_token
            }
        )
    
    raise InvalidToken()

@auth_router.get("/me", response_model=UserBooks)
async def get_current_user(user: UserModel = Depends(get_current_user), _: bool= Depends(role_checker)):
    return user

@auth_router.get("/logout", status_code=status.HTTP_200_OK)
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={"message": "Logged out successfully"}
    )