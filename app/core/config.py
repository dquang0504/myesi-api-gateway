from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    REDIS_URL: str = os.getenv("REDIS_URL", "localhost:6379")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "myesi_secret_key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    class Config:
        env_file = ".env"


settings = Settings()
