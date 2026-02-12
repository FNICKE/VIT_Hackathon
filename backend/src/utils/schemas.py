from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime


# ============== AUTH SCHEMAS ==============
class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    wallet_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class ConnectWallet(BaseModel):
    wallet_address: str


# ============== GROUP SCHEMAS ==============
class CreateGroupRequest(BaseModel):
    name: str
    description: Optional[str] = ""


class GroupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    creator_id: str
    vault_address: Optional[str]
    created_at: datetime
    member_count: int = 0

    class Config:
        from_attributes = True


class GroupDetailResponse(GroupResponse):
    members: List['GroupMemberResponse'] = []
    expense_count: int = 0


# ============== GROUP MEMBER SCHEMAS ==============
class GroupMemberResponse(BaseModel):
    id: str
    user_id: str
    wallet_address: Optional[str]
    trust_score: float
    joined_at: datetime
    warning_count: int
    is_active: bool

    class Config:
        from_attributes = True


class AddMemberRequest(BaseModel):
    user_id: str


# ============== EXPENSE SCHEMAS ==============
class CreateExpenseRequest(BaseModel):
    group_id: str
    amount: float
    description: Optional[str] = ""


class ExpenseResponse(BaseModel):
    id: str
    group_id: str
    paid_by_id: str
    amount: float
    description: Optional[str]
    created_at: datetime
    settled: bool

    class Config:
        from_attributes = True


# ============== SETTLEMENT SCHEMAS ==============
class SettlementRequest(BaseModel):
    group_id: str


class SettlementResponse(BaseModel):
    settlement_id: str
    settlements: List[Dict]
    risk_scores: Dict[str, float]
    warnings: Dict[str, str]
    excluded_members: List[str]
    explanation: str


class SettlementDetailResponse(BaseModel):
    id: str
    group_id: str
    settlements: List[Dict]
    risk_scores: Dict[str, float]
    warnings: Dict[str, str]
    excluded_members: List[str]
    governance_actions: Dict
    onchain_results: Dict
    explanation: Optional[str]
    status: str
    created_at: datetime
    executed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============== HEALTH CHECK ==============
class HealthResponse(BaseModel):
    status: str
    message: str
