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
    CreateExpenseRequest, ExpenseResponse, SettlementRequest,
    SettlementResponse, SettlementDetailResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{group_id}/add", response_model=ExpenseResponse)
async def add_expense(group_id: str, req: CreateExpenseRequest, user_id: str, db: Session = Depends(get_db)):
    """Add an expense to a group"""
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user is member
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    expense = Expense(
        id=str(uuid.uuid4()),
        group_id=group_id,
        paid_by_id=user_id,
        amount=req.amount,
        description=req.description or ""
    )
    
    db.add(expense)
    db.commit()
    db.refresh(expense)
    
    return ExpenseResponse.from_orm(expense)


@router.get("/{group_id}", response_model=list[ExpenseResponse])
async def list_expenses(group_id: str, user_id: str, db: Session = Depends(get_db)):
    """List all expenses in a group"""
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user is member
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    
    expenses = db.query(Expense).filter(Expense.group_id == group_id).all()
    return [ExpenseResponse.from_orm(e) for e in expenses]
