# Imports
from typing import TypedDict, List, Dict, Optional
from datetime import datetime

# Core State for a Group AI Agent
class Member(TypedDict):
    user_id: str
    wallet_address: str
    trust_score: float          # 0.0 – 1.0
    joined_at: datetime

class Expense(TypedDict):
    expense_id: str
    paid_by: str                # user_id
    amount: float
    description: str
    timestamp: datetime


class GroupState(TypedDict):
    # Basic identifiers
    group_id: str
    group_name: str

    # Participants & activity
    members: List[Member]
    expenses: List[Expense]

    # Financial computations
    balances: Dict[str, float]          # user_id -> net balance
    optimized_settlements: List[Dict]   # TEX output, this later goes on-chain for execution

    # Risk & behavior analysis
    risk_scores: Dict[str, float]       # user_id -> risk score
    warning_levels: Dict[str, str]      # user_id -> LEVEL_1/2/3/NONE

    # Governance & decisions
    excluded_members: List[str]         # excluded for current cycle
    last_action: Optional[str]

    # Explainability 
    explanation: Optional[str]

    # Metadata
    last_updated: datetime
