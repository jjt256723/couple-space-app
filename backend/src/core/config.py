from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Storage
    oss_access_key_id: str | None = None
    oss_access_key_secret: str | None = None
    oss_bucket_name: str | None = None
    oss_endpoint: str | None = None

    cos_secret_id: str | None = None
    cos_secret_key: str | None = None
    cos_bucket_name: str | None = None
    cos_region: str | None = None

    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_bucket_name: str | None = None
    aws_region: str | None = None

    # Environment
    environment: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
