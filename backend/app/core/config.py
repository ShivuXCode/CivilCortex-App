from pydantic import AnyHttpUrl
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "CivilCortex Agentic API"
    API_V1_STR: str = "/api"
    BACKEND_CORS_ORIGINS: List[str] = [origin.strip() for origin in os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")]
    
    # AI configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://civilcortex:civilcortex@localhost/civilcortex")
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
    
    # Background Workers
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Storage
    STORAGE_ROOT: str = os.getenv("STORAGE_ROOT", "storage/images/")
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ROOT_USER: str = os.getenv("MINIO_ROOT_USER", "minioadmin")
    MINIO_ROOT_PASSWORD: str = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "civilcortex-images")

    # Demo Mode configuration
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    DEFAULT_DEMO_SCENARIO: str = os.getenv("DEFAULT_DEMO_SCENARIO", "hairline_crack")

settings = Settings()

if settings.ENVIRONMENT == "production" and settings.SECRET_KEY == "super-secret-key-change-in-production":
    raise ValueError("Insecure SECRET_KEY set in production environment")
