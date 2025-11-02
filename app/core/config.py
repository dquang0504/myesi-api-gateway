# app/core/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "myesi_secret_key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    
    # Elasticsearch / Audit Logging
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    ES_INDEX_PREFIX: str = os.getenv("ES_INDEX_PREFIX", "myesi-audit")
    MAX_BODY_CHARS: int = int(os.getenv("MAX_BODY_CHARS", "1000"))

    class Config:
        env_file = ".env"

settings = Settings()
