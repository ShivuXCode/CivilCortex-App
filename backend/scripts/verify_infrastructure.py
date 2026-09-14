import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
import redis
from minio import Minio
from minio.error import S3Error

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

def verify_postgres():
    url = os.getenv("DATABASE_URL", "sqlite:///./civilcortex.db")
    print(f"Connecting to DB: {url}")
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            print("✅ PostgreSQL (or SQLite) connected successfully!")
    except Exception as e:
        print(f"❌ DB connection failed: {e}")

def verify_redis():
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    print(f"Connecting to Redis: {url}")
    try:
        client = redis.Redis.from_url(url)
        client.ping()
        print("✅ Redis connected successfully!")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")

def verify_minio():
    url = os.getenv("MINIO_URL", "localhost:9000")
    access = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    print(f"Connecting to MinIO: {url}")
    try:
        client = Minio(url, access_key=access, secret_key=secret, secure=False)
        buckets = client.list_buckets()
        print(f"✅ MinIO connected successfully! Found {len(buckets)} buckets.")
    except Exception as e:
        print(f"❌ MinIO connection failed: {e}")

if __name__ == "__main__":
    print("--- Verifying Phase 1 Infrastructure ---")
    verify_postgres()
    verify_redis()
    verify_minio()
