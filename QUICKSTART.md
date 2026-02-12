# 🚀 Quick Start Guide - AlgoSettler

## Prerequisites
- Python 3.13+
- Node.js & npm
- Git

---

## Backend Setup (Backend Service)

### 1️⃣ Navigate to backend directory
```bash
cd backend
```

### 2️⃣ Activate virtual environment
```bash
# Windows
backend_venv\Scripts\activate

# macOS/Linux
source backend_venv/bin/activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables
Create/verify `.env` file in backend directory with:
```
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./test.db
REDIS_HOST=localhost
REDIS_PORT=6379
GROQ_API_KEY=your-groq-key
GEMINI_API_KEY=your-gemini-key
ALGO_ADDRESS=your-algorand-address
PRIVATE_KEY=your-private-key
```

### 5️⃣ Start backend server
```bash
python -m uvicorn app:app --reload --port 8000
```

✅ Backend running at: **http://localhost:8000**

---

## Frontend Setup (React Application)

### 1️⃣ Navigate to frontend directory
```bash
cd frontend
```

### 2️⃣ Install dependencies
```bash
npm install
```

### 3️⃣ Configure environment variables
Create `.env.local` file with:
```
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

### 4️⃣ Start frontend development server
```bash
npm run dev
```

✅ Frontend running at: **http://localhost:5173**

---

## Testing the System

### 1️⃣ Run Backend Tests
```bash
cd backend
python -m pytest tests/test_api.py -v
```

### 2️⃣ Manual API Testing with cURL

**Register a new user:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

**Create a group:**
```bash
curl -X POST http://localhost:8000/api/groups/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"name":"Weekend Trip","description":"Split expenses for the trip"}'
```

### 3️⃣ Manual Frontend Testing

1. Open http://localhost:5173 in browser
2. Click "Register"
3. Create account with email/password
4. Should redirect to Dashboard
5. Click "Create Group"
6. Add group name and members
7. Add expenses
8. Click "Calculate Settlement"
9. Review AI-powered settlement recommendations

---

## API Documentation

### Automatic API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/wallet/connect` - Link wallet

#### Groups
- `POST /api/groups/create` - Create expense group
- `GET /api/groups` - List all groups
- `GET /api/groups/{id}` - Get group details
- `POST /api/groups/{id}/members` - Add member
- `DELETE /api/groups/{id}/members/{uid}` - Remove member

#### Expenses
- `POST /api/expenses/{group_id}/add` - Record expense
- `GET /api/expenses/{group_id}` - List expenses

#### Settlements (AI-Powered)
- `POST /api/settlements/calculate` - Calculate optimal settlement
- `GET /api/settlements/{id}` - Get settlement results
- `POST /api/settlements/{id}/execute` - Execute on blockchain

---

## Troubleshooting

### Issue: "No module named 'app'"
**Solution**: Ensure you're in the `backend` directory when running pytest

### Issue: "Cannot connect to localhost:5173"
**Solution**: Make sure frontend dev server is running: `npm run dev`

### Issue: "CORS error in frontend"
**Solution**: Verify VITE_API_URL in .env.local matches backend URL

### Issue: "JWT token expired"
**Solution**: Login again to get a fresh token (30-minute expiry)

### Issue: "Database locked"
**Solution**: Delete `test.db` and restart backend

### Issue: "No module named 'langchain'"
**Solution**: Run `pip install -r requirements.txt` again

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│         Frontend (React + Vite on :5173)           │
│      Login → Register → Dashboard → Groups → Expenses
└────────────────────┬────────────────────────────────┘
                     │ HTTP + JWT
                     ↓
┌─────────────────────────────────────────────────────┐
│    Backend (FastAPI + Uvicorn on :8000)             │
│  • 27 API Endpoints                                 │
│  • SQLAlchemy ORM                                   │
│  • JWT Authentication                              │
│  • LangGraph AI Orchestration                       │
└────┬──────────────────────────────┬─────────────────┘
     │                              │
     ↓ SQLAlchemy                   ↓ LangGraph
┌──────────────────┐        ┌─────────────────────┐
│    Database      │        │   AI Pipeline       │
│  (SQLite/PG)     │        │  8-Node Orchestration
│  6 Tables        │        │  Risk Analysis      │
│  Relationships   │        │  LLM Decisions      │
└──────────────────┘        │  Blockchain Exec    │
                            └─────────┬───────────┘
                                      │
                                      ↓ Algorand SDK
                                   ┌──────────────┐
                                   │   Blockchain │
                                   │  (Algorand)  │
                                   │  Testnet     │
                                   └──────────────┘
```

---

## Development Workflow

### Adding a New API Endpoint

1. **Define Schema** in `src/utils/schemas.py`:
```python
class MyRequest(BaseModel):
    field: str
```

2. **Create Route** in `src/routes/my_routes.py`:
```python
@router.post("/my-endpoint")
async def my_endpoint(data: MyRequest, db: Session = Depends(get_db)):
    # Logic here
    return {"result": "success"}
```

3. **Import in app.py**:
```python
from src.routes import my_routes
app.include_router(my_routes.router, prefix="/api")
```

4. **Test with:**
```bash
curl -X POST http://localhost:8000/api/my-endpoint \
  -H "Content-Type: application/json" \
  -d '{"field":"value"}'
```

---

## Database Migrations

### Create Migration
```bash
alembic revision --autogenerate -m "Add new table"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback
```bash
alembic downgrade -1
```

---

## Production Deployment

### Docker Build
```bash
docker build -t algosettler:latest .
docker run -p 8000:8000 algosettler:latest
```

### Environment Variables for Production
```bash
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_HOST=redis-prod.example.com
SECRET_KEY=<secure-random-key>
```

### Cloud Deployment
- **AWS**: Use ECS/Fargate with RDS PostgreSQL
- **GCP**: Deploy to Cloud Run with Cloud SQL
- **Azure**: Use App Service with Database for PostgreSQL

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `backend/app.py` | Main FastAPI application |
| `backend/src/models/models.py` | Database models |
| `backend/src/routes/*.py` | API route handlers |
| `backend/src/utils/auth.py` | Authentication logic |
| `backend/ai_agent/graph.py` | LangGraph orchestration |
| `frontend/src/config/api.js` | API client configuration |
| `frontend/src/pages/Login.jsx` | Login component |
| `frontend/src/pages/Register.jsx` | Registration component |
| `backend/requirements.txt` | Python dependencies |
| `frontend/package.json` | Node dependencies |

---

## Support & Resources

- **API Docs**: http://localhost:8000/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **React Docs**: https://react.dev/
- **LangChain Docs**: https://python.langchain.com/

---

**✅ System Ready for Development and Testing!**

Start with the Quick Start commands above, then visit http://localhost:5173 in your browser.
