from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import sys
import os
import logging

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from src.config.db import get_db
from src.models.models import Group, GroupMember, Expense, Settlement, User
from src.utils.schemas import (
    SettlementRequest, SettlementResponse, SettlementDetailResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/calculate", response_model=SettlementResponse)
async def calculate_settlement(req: SettlementRequest, user_id: str, db: Session = Depends(get_db)):
    """Calculate settlement for a group using LangGraph"""
    
    # Fetch group
    group = db.query(Group).filter(Group.id == req.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user is a member
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == req.group_id,
        GroupMember.user_id == user_id
    ).first()
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    try:
        # Import LangGraph here to avoid circular imports
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../backend'))
        from ai_agent.graph import build_graph
        
        # Fetch all data for the group
        members = db.query(GroupMember).filter(GroupMember.group_id == req.group_id).all()
        expenses = db.query(Expense).filter(
            Expense.group_id == req.group_id,
            Expense.settled == False
        ).all()
        
        # Build state for LangGraph
        from ai_agent.state import GroupState
        
        state: GroupState = {
            "group_id": group.id,
            "group_name": group.name,
            "members": [
                {
                    "user_id": m.user_id,
                    "wallet_address": m.wallet_address or "",
                    "trust_score": m.trust_score,
                    "joined_at": m.joined_at
                }
                for m in members
            ],
            "expenses": [
                {
                    "expense_id": e.id,
                    "paid_by": e.paid_by_id,
                    "amount": e.amount,
                    "description": e.description or "",
                    "timestamp": e.created_at
                }
                for e in expenses
            ],
            "balances": {},
            "optimized_settlements": [],
            "risk_scores": {},
            "warning_levels": {},
            "excluded_members": [],
            "last_action": None,
            "explanation": None,
            "last_updated": datetime.utcnow(),
            "warning_counts": {},
            "governance_actions": {},
            "onchain_results": {}
        }
        
        # Run LangGraph
        graph = build_graph()
        result = graph.invoke(state)
        
        # Save settlement to database
        settlement = Settlement(
            id=str(uuid.uuid4()),
            group_id=group.id,
            settlements=result.get("optimized_settlements", []),
            risk_scores=result.get("risk_scores", {}),
            warnings=result.get("warning_levels", {}),
            excluded_members=result.get("excluded_members", []),
            governance_actions=result.get("governance_actions", {}),
            onchain_results=result.get("onchain_results", {}),
            explanation=result.get("explanation", ""),
            status="pending"
        )
        db.add(settlement)
        db.commit()
        db.refresh(settlement)
        
        return SettlementResponse(
            settlement_id=settlement.id,
            settlements=settlement.settlements,
            risk_scores=settlement.risk_scores,
            warnings=settlement.warnings,
            excluded_members=settlement.excluded_members,
            explanation=settlement.explanation or "Settlement calculated successfully"
        )
        
    except Exception as e:
        logger.error(f"Settlement calculation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Settlement calculation failed: {str(e)}"
        )


@router.get("/{settlement_id}", response_model=SettlementDetailResponse)
async def get_settlement(settlement_id: str, user_id: str, db: Session = Depends(get_db)):
    """Get settlement details"""
    
    settlement = db.query(Settlement).filter(Settlement.id == settlement_id).first()
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    
    # Check if user is member of the group
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == settlement.group_id,
        GroupMember.user_id == user_id
    ).first()
    if not is_member:
        raise HTTPException(status_code=403, detail="Not authorized to view this settlement")
    
    return SettlementDetailResponse.from_orm(settlement)


@router.post("/{settlement_id}/execute")
async def execute_settlement(settlement_id: str, user_id: str, db: Session = Depends(get_db)):
    """Execute the settlement on Algorand"""
    
    settlement = db.query(Settlement).filter(Settlement.id == settlement_id).first()
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    
    # Check if user is creator of the group
    group = db.query(Group).filter(Group.id == settlement.group_id).first()
    if group.creator_id != user_id:
        raise HTTPException(status_code=403, detail="Only group creator can execute settlement")
    
    if settlement.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot execute {settlement.status} settlement"
        )
    
    try:
        # TODO: Execute on Algorand blockchain
        # For now, mark as executed
        settlement.status = "executed"
        settlement.executed_at = datetime.utcnow()
        
        # Mark expenses as settled
        expenses = db.query(Expense).filter(Expense.group_id == settlement.group_id).all()
        for exp in expenses:
            exp.settled = True
        
        db.commit()
        
        return {
            "status": "executed",
            "settlement_id": settlement.id,
            "message": "Settlement executed successfully"
        }
    except Exception as e:
        settlement.status = "failed"
        db.commit()
        logger.error(f"Settlement execution failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Settlement execution failed: {str(e)}"
        )
