from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import uuid

from ai_agent.graph import build_graph
from ai_agent.state import GroupState

app = FastAPI(title="Smart Expense Vault API")

# In-Memory Storage (Replace with DB in production)

users_db = {}
groups_db = {}
expenses_db = {}
settlements_db = {}

graph = build_graph()

# Pydantic Models

class LoginRequest(BaseModel):
    email: str
    password: str


class WalletRequest(BaseModel):
    user_id: str
    wallet_address: str


class CreateGroupRequest(BaseModel):
    group_name: str
    user_id: str
    rules: Optional[Dict] = {}


class AddMemberRequest(BaseModel):
    user_id: str


class AddExpenseRequest(BaseModel):
    group_id: str
    paid_by: str
    amount: float
    description: Optional[str] = ""
    split_among: Optional[List[str]] = None


class SettlementRequest(BaseModel):
    group_id: str


# AUTH

@app.post("/auth/login")
def login(req: LoginRequest):

    if req.email in users_db:
        return {"message": "Login successful", "user_id": users_db[req.email]["id"]}

    user_id = str(uuid.uuid4())

    users_db[req.email] = {
        "id": user_id,
        "email": req.email,
        "password": req.password,
        "wallet": None,
        "created_at": datetime.utcnow().isoformat()
    }

    return {"message": "User created", "user_id": user_id}


@app.post("/auth/connect-wallet")
def connect_wallet(req: WalletRequest):

    for user in users_db.values():
        if user["id"] == req.user_id:
            user["wallet"] = req.wallet_address
            return {"message": "Wallet connected"}

    raise HTTPException(status_code=404, detail="User not found")


# GROUPS
@app.post("/groups/create")
def create_group(req: CreateGroupRequest):

    group_id = str(uuid.uuid4())

    groups_db[group_id] = {
        "id": group_id,
        "name": req.group_name,
        "creator": req.user_id,
        "members": [req.user_id],
        "rules": req.rules,
        "created_at": datetime.now().isoformat(),
    }

    return {"message": "Group created", "group_id": group_id}


@app.post("/groups/{group_id}/members")
def add_member(group_id: str, req: AddMemberRequest):

    if group_id not in groups_db:
        raise HTTPException(status_code=404, detail="Group not found")

    if req.user_id not in groups_db[group_id]["members"]:
        [groups_db[group_id]["members"]].append(req.user_id)

    return {"members": groups_db[group_id]["members"]}


# EXPENSES
@app.post("/expenses/add")
def add_expense(req: AddExpenseRequest):

    if req.group_id not in groups_db:
        raise HTTPException(status_code=404, detail="Group not found")

    expense_id = str(uuid.uuid4())

    expenses_db[expense_id] = {
        "id": expense_id,
        "group_id": req.group_id,
        "paid_by": req.paid_by,
        "amount": req.amount,
        "description": req.description,
        "split_among": req.split_among or groups_db[req.group_id]["members"],
        "created_at": datetime.utcnow(),
        "settled": False
    }

    return {"message": "Expense added", "expense_id": expense_id}


# SETTLEMENT (LangGraph Integrated)
@app.post("/settlements/calculate")
def calculate_settlement(req: SettlementRequest):

    if req.group_id not in groups_db:
        raise HTTPException(status_code=404, detail="Group not found")

    group = groups_db[req.group_id]
    group_expenses = [
        exp for exp in expenses_db.values()
        if exp["group_id"] == req.group_id and not exp["settled"]
    ]

    # Build GroupState for LangGraph
    state: GroupState = {
        "group_id": req.group_id,
        "group_name": group["name"],
        "members": [
            {
                "user_id": member,
                "wallet_address": "",
                "trust_score": 0.5,
                "joined_at": datetime.utcnow()
            }
            for member in group["members"]
        ],
        "expenses": group_expenses,
        "balances": {},
        "optimized_settlements": [],
        "risk_scores": {},
        "warning_levels": {},
        "excluded_members": [],
        "last_action": None,
        "explanation": None,
        "last_updated": datetime.utcnow()
    }

    result = graph.invoke(state)

    settlement_id = str(uuid.uuid4())

    settlements_db[settlement_id] = {
        "id": settlement_id,
        "group_id": req.group_id,
        "settlements": result["optimized_settlements"],
        "risk_scores": result["risk_scores"],
        "warnings": result["warning_levels"],
        "excluded_members": result["excluded_members"],
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }

    return {
        "settlement_id": settlement_id,
        "settlements": result["optimized_settlements"],
        "risk_scores": result["risk_scores"],
        "warnings": result["warning_levels"],
        "excluded_members": result["excluded_members"]
    }

# HEALTHCHECK
@app.get("/health")
def health():
    return {"status": "OK, good to go", "timestamp": datetime.now().isoformat()}