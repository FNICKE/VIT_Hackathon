import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import redis

# Load environment variables from .env file
load_dotenv()

# --- SQL Database Setup (MySQL via SQLAlchemy) ---
# We use the DATABASE_URL directly as it's already formatted for mysql+pymysql
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    # Fallback construction if DATABASE_URL is missing but individual vars exist
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "algosettler")
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # pool_pre_ping helps recover from "MySQL server has gone away" errors (common in XAMPP)
    pool_pre_ping=True,
    echo=os.getenv("DEBUG", "False").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """Initialize database tables"""
    # Import models here to avoid circular imports
    # Ensure your models inherit from this 'Base'
    from src.models.models import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get the DB session for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Redis Setup ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0, # Defaulting to DB 0 as per your .env
        decode_responses=True,
        socket_connect_timeout=1 # Prevents the app from hanging if Redis is down
    )
    redis_client.ping()
except Exception as e:
    print(f"⚠️ Redis connection failed: {e}. Caching will be disabled.")
    redis_client = None

def get_redis():
    return redis_client