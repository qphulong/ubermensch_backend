from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
import uuid
from src.core.config import settings
import logging

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_token(user_data: dict, refresh: bool = False):
    payload = {}

    payload['user'] = user_data
    payload['exp'] = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES if not refresh else settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token, 
            key=settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return token_data
    except JWTError as e:
        logging.error(f"Token decoding error: {e}")
        return None

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)