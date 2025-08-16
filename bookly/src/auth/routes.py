from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta, datetime
from .schemas import CreateUser, UserModel, UserLogin, UserBooks, Email, PasswordResetRequest, PasswordReset
from .service import UserService
from .utils import create_access_token, verify_password, create_url_safe_token, decode_url_safe_token, generate_hash
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.errors import UserAlreadyExists, InvalidCredentials, InvalidToken, UserNotFound
from src.mail import mail, create_message
from src.config import Config

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

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: CreateUser, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)
    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h1>Verify your email</h1>
    <p>Please click the link below to verify your email address:</p>
    <a href="{link}">Verify Email</a>
    """
    message = create_message([email], "Verify Your Email - Bookly", html_message)

    await mail.send_message(message)
    return {
        "message": "Account Created Successfully! Check your email to verify your account.",
        "user": new_user
    }

@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    email = token_data.get("email")

    if email:
        user = await user_service.get_user_by_email(email, session)
        if not user:
            raise UserNotFound()
        
        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={
                "message": "Email verified successfully"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={
            "message": "Something went wrong during verification!"
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

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

@auth_router.post("/reset_password_request")
async def reset_password_request(email: PasswordResetRequest):
    token = create_url_safe_token({"email": email.email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/reset_password/{token}"

    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click the link below to reset your password:</p>
    <a href="{link}">Reset Password</a>
    """
    message = create_message([email.email], "Reset Your Password - Bookly", html_message)

    await mail.send_message(message)
    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password."
        },
        status_code= status.HTTP_200_OK
    )

@auth_router.post("/reset_password/{token}")
async def reset_password(token: str, password_data: PasswordReset, session: AsyncSession = Depends(get_session)):
    if password_data.password != password_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    
    token_data = decode_url_safe_token(token)
    email = token_data.get("email")

    if email:
        user = await user_service.get_user_by_email(email, session)
        if not user:
            raise UserNotFound()
        
        await user_service.update_user(user, {"password": generate_hash(password_data.password)}, session)

        return JSONResponse(
            content={
                "message": "Password reset successful."
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={
            "message": "Something went wrong during password reset!"
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )