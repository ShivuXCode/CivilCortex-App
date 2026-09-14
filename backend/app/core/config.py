from pydantic import AnyHttpUrl
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "CivilCortex Agentic API"
    API_V1_STR: str = "/api"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # AI configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://civilcortex:civilcortex@localhost/civilcortex")
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Storage
    STORAGE_ROOT: str = os.getenv("STORAGE_ROOT", "storage/images/")

    # Demo Mode configuration
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    DEFAULT_DEMO_SCENARIO: str = os.getenv("DEFAULT_DEMO_SCENARIO", "hairline_crack")

settings = Settings()

