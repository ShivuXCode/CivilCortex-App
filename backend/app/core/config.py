from pydantic import AnyHttpUrl, field_validator
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "CivilCortex Agentic API"
    API_V1_STR: str = "/api"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # AI configuration
    GEMINI_API_KEY: str = ""
    
    # Database configuration
    DATABASE_URL: str = "postgresql://civilcortex:civilcortex@localhost/civilcortex"
    TEST_DATABASE_URL: str = "sqlite:///./test.db"
    
    # Background Workers
    REDIS_URL: str = "redis://localhost:6379/0"
    
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    # 60-minute expiry: short-lived tokens limit the damage window of token theft.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Storage
    STORAGE_ROOT: str = "storage/images/"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "civilcortex-images"

    # ML Thresholds
    ML_MIN_AREA_THRESHOLD: int = 50

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()

if settings.ENVIRONMENT == "production" and settings.SECRET_KEY == "super-secret-key-change-in-production":
    raise ValueError("Insecure SECRET_KEY set in production environment")
