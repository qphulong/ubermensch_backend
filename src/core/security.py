from fastapi import Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
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
            token, 
            key=settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return token_data
    except JWTError as e:
        logging.error(f"Token decoding error: {e}")
        return None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials
        if not self.valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication credentials"
            )
        
        token_data = decode_token(token)
        self.verify_token_data(token_data)

        return token_data

    def valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return token_data is not None
    
    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Subclasses must implement this method")
    
class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a valid access token"
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a valid refresh token"
            )