import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# CRITICAL: Add parent directories to path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CRITICAL: Import models BEFORE anything else to register them with declarative_base
from src.models.models import Base, User, Group, GroupMember, Expense, Settlement, AuditLog

# Setup test database URL
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_db_temp.db"

# Create test engine 
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Create all tables in test database BEFORE importing app
print("\n[SETUP] Creating test database tables...")
Base.metadata.create_all(bind=test_engine)
print("[SETUP] Test database tables created successfully!\n")

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# NOW import app and routes
from app import app
from src.config.db import get_db
from src.utils.auth import hash_password, create_access_token

# Import TestClient AFTER app is loaded
from fastapi.testclient import TestClient

# Override get_db dependency with test database
def override_get_db():
    """Override database dependency for tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply the override
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

print("[SETUP] Test client initialized successfully!\n")


# ============== FIXTURES ==============
@pytest.fixture(autouse=True)
def setup_database():
    """Setup and teardown database for each test"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def test_user():
    """Create a test user"""
    db = TestingSessionLocal()
    user = User(
        id="test-user-1",
        email="test@example.com",
        password_hash=hash_password("testpass123"),
        wallet_address="4BG6P2JDQXYWFJ4ERCSY5JINE6DSN55NXUJS5CU4Z27MQCRHXXGTUAVT24"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def test_token(test_user):
    """Create a test JWT token"""
    return create_access_token(data={"sub": test_user.id})


# ============== HEALTH CHECK TESTS ==============
def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ============== AUTH TESTS ==============
def test_register_new_user():
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        json={"email": "newuser@example.com", "password": "mypass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@example.com"


def test_register_duplicate_email(test_user):
    """Test registration with duplicate email"""
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "newpass123"}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(test_user):
    """Test user login"""
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["id"] == test_user.id


def test_login_invalid_password(test_user):
    """Test login with wrong password"""
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_get_profile(test_user, test_token):
    """Test getting user profile"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


# ============== GROUP TESTS ==============
def test_create_group(test_user, test_token):
    """Test creating a group"""
    response = client.post(
        "/api/groups/create",
        json={"name": "Test Group", "description": "A test group"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Group"
    assert data["member_count"] == 1


def test_list_groups(test_user, test_token):
    """Test listing user's groups"""
    # Create a group first
    client.post(
        "/api/groups/create",
        json={"name": "Group 1"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # List groups
    response = client.get(
        "/api/groups",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Group 1"


def test_get_group(test_user, test_token):
    """Test getting group details"""
    # Create a group first
    create_resp = client.post(
        "/api/groups/create",
        json={"name": "Test Group"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    group_id = create_resp.json()["id"]
    
    # Get group
    response = client.get(
        f"/api/groups/{group_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Group"


# ============== EXPENSE TESTS ==============
def test_add_expense(test_user, test_token):
    """Test adding an expense"""
    # Create a group first
    create_resp = client.post(
        "/api/groups/create",
        json={"name": "Test Group"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    group_id = create_resp.json()["id"]
    
    # Add expense
    response = client.post(
        f"/api/expenses/{group_id}/add",
        json={"amount": 100.50, "description": "Lunch"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100.50
    assert data["description"] == "Lunch"


def test_list_expenses(test_user, test_token):
    """Test listing expenses"""
    # Create a group and add expense
    create_resp = client.post(
        "/api/groups/create",
        json={"name": "Test Group"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    group_id = create_resp.json()["id"]
    
    client.post(
        f"/api/expenses/{group_id}/add",
        json={"amount": 100, "description": "Lunch"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # List expenses
    response = client.get(
        f"/api/expenses/{group_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["amount"] == 100.0


# ============== SETTLEMENT TESTS ==============
def test_calculate_settlement(test_user, test_token):
    """Test settlement calculation"""
    # Create a group and add expense
    create_resp = client.post(
        "/api/groups/create",
        json={"name": "Test Group"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    group_id = create_resp.json()["id"]
    
    # Add expense
    client.post(
        f"/api/expenses/{group_id}/add",
        json={"amount": 100, "description": "Test"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    # Calculate settlement
    response = client.post(
        "/api/settlements/calculate",
        json={"group_id": group_id},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "settlement_id" in data
    assert "risk_scores" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
