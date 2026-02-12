from typing import TypedDict, List, Dict, Optional, Annotated
from datetime import datetime
import operator


# Helper type aliases (makes state cleaner and more readable)
UserID = str
WalletAddress = str
Amount = float
Currency = str          # e.g. "USD", "INR", "USDC", etc.
ExpenseID = str


class Member(TypedDict):
    user_id: UserID
    wallet_address: WalletAddress
    display_name: Optional[str]             # optional nickname / ENS / lens handle
    trust_score: float                      # 0.0 – 1.0 (updated by agent / votes / payments)
    risk_score: float                       # separate from trust (e.g. volatility, late payments)
    joined_at: datetime
    last_active: Optional[datetime]         # helps detect inactive/stale members
    role: str                               # e.g. "admin", "member", "observer"


class ExpenseSplit(TypedDict):
    """How one expense is divided among members"""
    user_id: UserID
    share: Amount                           # amount this user should pay/receive for this expense
    settled: bool                           # whether this split has been paid/settled
    settled_at: Optional[datetime]


class Expense(TypedDict):
    expense_id: ExpenseID
    created_by: UserID
    paid_by: UserID                         # who actually paid (may differ from creator)
    amount: Amount
    currency: Currency                      # important for multi-currency groups
    description: str
    timestamp: datetime
    involved_members: List[UserID]          # who participated in this expense
    splits: List[ExpenseSplit]              # detailed per-user breakdown
    receipt_url: Optional[str]              # IPFS / Arweave / cloud link
    status: str                             # "pending", "approved", "disputed", "settled"


class Settlement(TypedDict):
    """One atomic settlement instruction (usually goes on-chain)"""
    from_user: UserID
    to_user: UserID
    amount: Amount
    currency: Currency
    reason: str                             # e.g. "Expense #exp123 share", "Reimbursement"
    expense_ids: List[ExpenseID]            # which expenses this covers
    tx_hash: Optional[str]                  # filled after on-chain execution
    executed_at: Optional[datetime]


class GroupState(TypedDict):
    # ── Core identifiers ────────────────────────────────────────────────
    group_id: str
    group_name: str
    description: Optional[str]
    currency_default: Currency              # default currency for new expenses

    # ── Participants ────────────────────────────────────────────────────
    members: List[Member]
    excluded_members: List[UserID]          # temporarily or permanently excluded

    # ── Financial data ──────────────────────────────────────────────────
    expenses: List[Expense]

    # Current net balances (positive = owes group, negative = group owes)
    balances: Dict[UserID, Amount]

    # Pending / recommended settlements (usually produced by min-cost flow / TEX algo)
    pending_settlements: List[Settlement]

    # Already executed settlements (history)
    settlement_history: List[Settlement]

    # ── Risk, trust & moderation ────────────────────────────────────────
    trust_scores: Dict[UserID, float]       # can be different view from member.trust_score
    warning_levels: Dict[UserID, str]       # "NONE", "LEVEL_1", "LEVEL_2", "LEVEL_3", "BANNED"
    flagged_expenses: List[ExpenseID]       # disputed or suspicious

    # ── Governance & state machine ──────────────────────────────────────
    current_cycle: int                      # increment after settlements or monthly
    voting_threshold: float                 # e.g. 0.6 for majority
    last_major_action: Optional[str]        # "expense_added", "settlement_executed", etc.
    last_updated: datetime

    # ── Explainability & debugging (very useful for agents) ─────────────
    explanation: Optional[str]              # last agent's reasoning summary
    last_agent_thought: Optional[str]       # more detailed chain-of-thought if needed

    # ── Optional extensions / metadata ──────────────────────────────────
    settings: Dict[str, any]                # flexible key-value (notifications, visibility, etc.)
    version: int                            # schema version for future migrations