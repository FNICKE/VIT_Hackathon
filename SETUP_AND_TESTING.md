# AlgoSettler - Deployment & Testing Guide

## System Overview

This is a complete end-to-end AI-powered expense settlement system with Algorand blockchain integration.

### Architecture
```
Frontend (React/Vite) 
    ↓ (API Calls with JWT)
FastAPI Backend
    ↓
LangGraph AI Orchestration
    ├─ Compute Balances
    ├─ TEX Optimization
    ├─ Risk Analysis
    ├─ Warning System
    ├─ LLM Explanations
    ├─ Governance Decisions
    └─ Algorand Execution
    ↓
SQLite/PostgreSQL Database
```

## Setup Instructions

### 1. Backend Setup

#### Prerequisites
- Python 3.11+
- pip package manager

#### Installation Steps

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv backend_venv

# Activate virtual environment
# On Windows:
backend_venv\Scripts\activate
# On Mac/Linux:
source backend_venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (creates tables)
python -c "from src.config.db import init_db; init_db(); print('Database initialized!')"
```

#### Environment Configuration

Update `.env` file with your credentials:

```env
# Application
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-super-secret-key-change-this

# Database
DATABASE_URL=sqlite:///./test.db

# Algorand
PRIVATE_KEY=your-algorand-private-key
ALGO_ADDRESS=your-algorand-address
TREASURY_WALLET=treasury-wallet-address
ALGO_NODE_URL=https://testnet-api.algonode.cloud

# AI APIs
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key
```

#### Run Backend

```bash
# Development (with auto-reload)
python app.py

# Production
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs` (Swagger UI)

### 2. Frontend Setup

#### Prerequisites
- Node.js 16+
- npm or yarn

#### Installation Steps

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env.local file (already created, update if needed)
# VITE_API_URL=http://localhost:8000/api
# VITE_GOOGLE_CLIENT_ID=your-google-client-id

# Run development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### 3. Database Setup

#### SQLite (Development - Already Configured)
- Database is automatically created at `backend/test.db`
- Tables are created on first app startup

#### PostgreSQL (Production)

```bash
# Create database
createdb algosettler

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/algosettler

# Run migrations (if using Alembic)
alembic upgrade head
```

---

## Testing the Application

### 1. Automated Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### 2. Manual API Testing with cURL

#### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "TestPass123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "wallet_address": null,
    "created_at": "2026-02-12T..."
  }
}
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "TestPass123"
  }'
```

#### Create Group (Need Authorization)
```bash
curl -X POST http://localhost:8000/api/groups/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Dinner with Friends",
    "description": "Friday night dinner split"
  }'
```

#### Add Expense
```bash
curl -X POST http://localhost:8000/api/expenses/GROUP_ID/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "amount": 150.50,
    "description": "Restaurant bill"
  }'
```

#### Calculate Settlement (LangGraph)
```bash
curl -X POST http://localhost:8000/api/settlements/calculate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "group_id": "GROUP_ID"
  }'
```

### 3. Frontend Testing

#### Login Flow
1. Visit `http://localhost:5173/login`
2. Enter credentials:
   - Email: `user@example.com`
   - Password: `TestPass123`
3. Should redirect to dashboard

#### User Journey
1. **Login** → Redirects to `/dashboard`
2. **Create Group** → Click "Create New" in Groups page
3. **Add Members** → Add other users to the group
4. **Add Expenses** → Record expenses
5. **Calculate Settlement** → Run LangGraph AI
6. **View Results** → See settlements, risk scores, and recommendations

---

## Critical Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/auth/register` | No | Register new user |
| POST | `/api/auth/login` | No | Login user |
| GET | `/api/auth/me` | Yes | Get current user |
| POST | `/api/groups/create` | Yes | Create expense group |
| GET | `/api/groups` | Yes | List user's groups |
| GET | `/api/groups/{id}` | Yes | Get group details |
| POST | `/api/expenses/{group_id}/add` | Yes | Add expense |
| GET | `/api/expenses/{group_id}` | Yes | List expenses |
| POST | `/api/settlements/calculate` | Yes | Run LangGraph calculation |
| GET | `/api/settlements/{id}` | Yes | Get settlement details |
| POST | `/api/settlements/{id}/execute` | Yes | Execute settlement |

---

## Troubleshooting

### Backend Issues

#### Database Not Found
```bash
# Reinitialize database
python -c "from src.config.db import init_db; init_db()"
```

#### Import Errors
```bash
# Add backend to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Port Already in Use
```bash
# Use different port
uvicorn app:app --host 0.0.0.0 --port 8001
```

### Frontend Issues

#### CORS Errors
- Ensure backend is running on `http://localhost:8000`
- Check `.env.local` has correct `VITE_API_URL`
- Verify CORS middleware in `app.py` includes frontend origin

#### API Not Responding
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check logs in backend terminal
# Should show: GET /health - 200 OK
```

---

## Production Deployment

### Backend (Docker)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment for Production
```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-long-random-secret-key
DATABASE_URL=postgresql://user:password@host:5432/algosettler
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
PROD_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Frontend (Deployment)
```bash
# Build for production
npm run build

# Output goes to 'dist/' folder
# Deploy to Vercel, Netlify, or your server
```

---

## Performance Optimization

### Backend
- Implement caching with Redis for settlement calculations
- Use connection pooling for database
- Add rate limiting to prevent abuse
- Implement pagination for list endpoints

### Frontend
- Code splitting with React.lazy()
- Image optimization
- Enable gzip compression
- Minify CSS and JavaScript

---

## Security Checklist

- [x] Password hashing with bcrypt
- [x] JWT token authentication
- [x] CORS configuration
- [x] Input validation with Pydantic
- [x] Environment variables for secrets
- [ ] Rate limiting implementation
- [ ] Request logging and monitoring
- [ ] HTTPS for production
- [ ] Regular security audits
- [ ] Dependency updates

---

## Support & Documentation

- **Swagger API Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **GitHub**: Your repository link
- **Issues**: Report bugs via GitHub Issues

---

## Contributors

Built with ❤️ for VIT Hackathon 2026
