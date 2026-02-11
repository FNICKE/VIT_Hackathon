import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth_routes import router as auth_router
# from routes.algo_routes import router as algo_router # Example for future routes

app = FastAPI(
    title="AI & Blockchain API",
    description="FastAPI backend for React, Algorand, and LangChain",
    version="1.0.0"
)

# --- CORS Configuration ---
# This allows your React frontend (localhost:5173) to talk to this API
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# --- Register Routes ---
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
# app.include_router(algo_router, prefix="/api/blockchain", tags=["Algorand"])

@app.get("/")
async def health_check():
    return {"status": "online", "message": "Server is running smoothly"}

if __name__ == "__main__":
    # This allows you to run the file directly with 'python app.py'
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)