# app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "MyESI API Gateway"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/myesi"  # apne DB ke hisaab se update karein
    SECRET_KEY: str = "myesi_secret_key"  # JWT secret key
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
