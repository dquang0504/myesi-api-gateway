from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "MyESI API Gateway"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/myesi"
    REDIS_URL: str = "redis://redis:6379/0"
    SSL_CERT_PATH: str = "certs/cert.pem"
    SSL_KEY_PATH: str = "certs/key.pem"

    class Config:
        env_file = ".env"


settings = Settings()
