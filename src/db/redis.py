import redis
from src.core.config import settings

token_blocklist = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0
)

def add_token_to_blocklist(jti: str) -> None:
    token_blocklist.set(jti, "blocked", ex=settings.JTI_EXPIRATION)

def is_token_blocked(jti: str) -> bool:
    jti = token_blocklist.get(jti)
    return jti is not None