from passlib.context import CryptContext
from datetime import timedelta, datetime
from itsdangerous import URLSafeTimedSerializer
import jwt
import uuid
import logging

from src.config import Config

ACCESS_TOKEN_EXPIRY = 3600

pwd_context = CryptContext(schemes=["bcrypt"])

def generate_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload= payload,
        key= Config.JWT_SECRET,
        algorithm= Config.JWT_ALGORITHM
    )
    return token

def verify_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
    
serializer = URLSafeTimedSerializer(Config.JWT_SECRET, salt="email-verification")

def create_url_safe_token(data: dict):
    token = serializer.dumps(data)
    return token

def decode_url_safe_token(token: str):
    try:
        return serializer.loads(token)
    except Exception as e:
        logging.exception(e)
        return None