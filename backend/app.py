import os
import sys
import logging
import time
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Set up logging with a cleaner format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AlgoSettler")

# Import database and models
from src.config.db import engine, init_db, SessionLocal, get_db
from src.models.models import Base, User
from src.utils.auth import decode_token
from src.utils.schemas import HealthResponse

# Import routes
from src.routes import auth_routes, group_routes, expense_routes, settlement_routes

# ============== DATABASE CONNECTION CHECK ==============
def check_db_connection():
    """Verify database is reachable and initialized"""
    print("\n" + "="*50)
    print("🔍 CHECKING DATABASE CONNECTION...")
    print("="*50)
    
    start_time = time.time()
    try:
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        
        # Initialize tables
        init_db()
        
        elapsed = round((time.time() - start_time) * 1000, 2)
        print(f"✅ DATABASE: Connected to MySQL successfully!")
        print(f"✅ TABLES: All schema tables verified/created.")
        print(f"⏱️  LATENCY: {elapsed}ms")
        print("="*50 + "\n")
        return True
    except Exception as e:
        print(f"❌ DATABASE ERROR: Could not connect to MySQL.")
        print(f"🚨 DETAILS: {e}")
        print("="*50 + "\n")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run DB check
    db_up = check_db_connection()
    if not db_up:
        logger.error("System starting in degraded mode: Database is offline.")
    yield
    # Shutdown
    logger.info("AlgoSettler API shutting down...")

# Create FastAPI app
app = FastAPI(
    title="AlgoSettler API",
    description="AI-powered expense settlement with Algorand blockchain integration",
    version="1.0.0",
    lifespan=lifespan
)

# ... (CORS configuration remains the same) ...

# ============== AUTHENTICATION MIDDLEWARE ==============
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db = Depends(get_db)):
    """Extract and validate JWT token with injected DB session"""
    token = credentials.credentials
    user_id = decode_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Use the injected get_db dependency instead of creating a new SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user_id

# ... (Rest of your routes remain the same) ...

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"🚀 Starting AlgoSettler on http://{host}:{port}")
    uvicorn.run(
        "app:app", # Note: make sure your filename is actually app.py or main.py
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )