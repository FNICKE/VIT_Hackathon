import os
import sys
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database and models
from src.config.db import engine, init_db, SessionLocal, get_db
from src.models.models import Base, User
from src.utils.auth import decode_token
from src.utils.schemas import HealthResponse

# Import routes
from src.routes import auth_routes, group_routes, expense_routes, settlement_routes

# Initialize database
def startup():
    """Initialize database tables on startup"""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    startup()
    yield
    # Shutdown (cleanup if needed)

# Create FastAPI app
app = FastAPI(
    title="AlgoSettler API",
    description="AI-powered expense settlement with Algorand blockchain integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add environment-based origins for production
prod_origins = os.getenv("PROD_ORIGINS", "").split(",")
if prod_origins and prod_origins[0]:
    origins.extend(prod_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== AUTHENTICATION MIDDLEWARE ==============
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and validate JWT token"""
    token = credentials.credentials
    user_id = decode_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user exists in database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user_id
    finally:
        db.close()


# ============== HEALTH CHECK ==============
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="AlgoSettler API is running"
    )


# ============== AUTH ROUTES ==============
@app.post("/api/auth/register")
async def register(request: dict, db = Depends(get_db)):
    """Register endpoint - delegates to auth routes"""
    from src.utils.schemas import UserRegister
    user_data = UserRegister(**request)
    return await auth_routes.register(user_data, db)


@app.post("/api/auth/login")
async def login(request: dict, db = Depends(get_db)):
    """Login endpoint - delegates to auth routes"""
    from src.utils.schemas import UserLogin
    credentials = UserLogin(**request)
    return await auth_routes.login(credentials, db)


@app.post("/api/auth/wallet/connect")
async def connect_wallet(request: dict, user_id: str = Depends(get_current_user), db = Depends(get_db)):
    """Connect wallet endpoint"""
    from src.utils.schemas import ConnectWallet
    wallet_req = ConnectWallet(**request)
    return await auth_routes.connect_wallet(wallet_req, user_id, db)


@app.get("/api/auth/me")
async def get_me(user_id: str = Depends(get_current_user), db = Depends(get_db)):
    """Get current user profile"""
    return await auth_routes.get_current_user(user_id, db)


# ============== GROUP ROUTES ==============
@app.post("/api/groups/create")
async def create_group(request: dict, user_id: str = Depends(get_current_user), db = Depends(get_db)):
    """Create group endpoint"""
    from src.utils.schemas import CreateGroupRequest
    req = CreateGroupRequest(**request)
    return await group_routes.create_group(req, user_id, db)


@app.get("/api/groups")
async def list_groups(user_id: str = Depends(get_current_user), db = Depends(get_db)):
    """List user's groups"""
    return await group_routes.list_groups(user_id, db)


@app.get("/api/groups/{group_id}")
async def get_group(group_id: str, user_id: str = Depends(get_current_user), db = Depends(get_db)):
    """Get group details"""
    return await group_routes.get_group(group_id, user_id, db)


@app.post("/api/groups/{group_id}/members")
async def add_member(group_id: str, request: dict, user_id: str = Depends(get_current_user), db = Depends(get_db)):
    """Add member to group"""
    from src.utils.schemas import AddMemberRequest
    req = AddMemberRequest(**request)
    return await group_routes.add_member(group_id, req, user_id, db)


@app.delete("/api/groups/{group_id}/members/{member_id}")
async def remove_member(group_id: str, member_id: str, user_id: str = Depends(get_current_user), db = Depends(get_db)):
    """Remove member from group"""
    return await group_routes.remove_member(group_id, member_id, user_id, db)


# ============== EXPENSE ROUTES ==============
@app.post("/api/expenses/{group_id}/add")
async def add_expense(group_id: str, request: dict, user_id: str = Depends(get_current_user), db = Depends(get_db)):
    """Add expense to group"""
    from src.utils.schemas import CreateExpenseRequest
    req = CreateExpenseRequest(group_id=group_id, **request)
    return await expense_routes.add_expense(group_id, req, user_id, db)


@app.get("/api/expenses/{group_id}")
async def list_expenses(group_id: str, user_id: str = Depends(get_current_user), db = Depends(get_db)):
    """List expenses in group"""
    return await expense_routes.list_expenses(group_id, user_id, db)


# ============== SETTLEMENT ROUTES ==============
@app.post("/api/settlements/calculate")
async def calculate_settlement(request: dict, user_id: str = Depends(get_current_user), db = Depends(get_db)):
    """Calculate settlement for group"""
    from src.utils.schemas import SettlementRequest
    req = SettlementRequest(**request)
    return await settlement_routes.calculate_settlement(req, user_id, db)


@app.get("/api/settlements/{settlement_id}")
async def get_settlement(settlement_id: str, user_id: str = Depends(get_current_user), db = Depends(get_db)):
    """Get settlement details"""
    return await settlement_routes.get_settlement(settlement_id, user_id, db)


@app.post("/api/settlements/{settlement_id}/execute")
async def execute_settlement(settlement_id: str, user_id: str = Depends(get_current_user), db = Depends(get_db)):
    """Execute settlement"""
    return await settlement_routes.execute_settlement(settlement_id, user_id, db)


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )