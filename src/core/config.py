from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path
import yaml

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"
    ADMIN_EMAIL: str = ""
    ADMIN_GIT_LINK: str = ""
    ADMIN_GMAIL_APP_PASSWORD: str = ""
    OTP_EXPIRED_TIME: int = 3
    OTP_CLEANUP_INTERVAL: int =5
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    JTI_EXPIRATION: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def from_yaml(cls, yaml_path: str = "config.yaml") -> "Settings":
        settings = cls()
        yaml_path = Path(yaml_path)
        if yaml_path.exists():
            with open(yaml_path, "r") as f:
                yaml_config = yaml.safe_load(f) or {}
            if "otp" in yaml_config:
                settings.OTP_EXPIRED_TIME = yaml_config["otp"].get("expired_time", settings.OTP_EXPIRED_TIME)
                settings.OTP_CLEANUP_INTERVAL = yaml_config["otp"].get("cleanup_interval", settings.OTP_EXPIRED_TIME)

        return settings

settings = Settings.from_yaml("config.yaml")