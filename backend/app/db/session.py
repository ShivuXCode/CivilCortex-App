from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings
import os

# Check if we are running under pytest by looking for PYTEST_CURRENT_TEST
# This ensures tests automatically use the test database
is_testing = "PYTEST_CURRENT_TEST" in os.environ
db_url = settings.TEST_DATABASE_URL if is_testing else settings.DATABASE_URL

# For SQLite we need check_same_thread=False
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
