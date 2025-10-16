"""
Configuration settings for the MyESI API Gateway.
Handles environment variables and core app configuration.
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "MyESI API Gateway"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/myesi"  # Local dev DB
    REDIS_URL: str = "redis://redis:6379/0"
    SSL_CERT_PATH: str = "certs/cert.pem"
    SSL_KEY_PATH: str = "certs/key.pem"
    SECRET_KEY: str = "myesi_secret_key"
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
