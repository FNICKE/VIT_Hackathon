from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from src.config.db import get_db
from src.models.models import Group, GroupMember, User, Expense
from src.utils.schemas import (
    CreateGroupRequest, GroupResponse, GroupDetailResponse, AddMemberRequest
)

router = APIRouter()


@router.post("/create", response_model=GroupResponse)
async def create_group(req: CreateGroupRequest, user_id: str, db: Session = Depends(get_db)):
    """Create a new expense group"""
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    group_id = str(uuid.uuid4())
    
    # Create group
    group = Group(
        id=group_id,
        name=req.name,
        description=req.description or "",
        creator_id=user_id
    )
    
    # Add creator as first member
    member = GroupMember(
        id=str(uuid.uuid4()),
        group_id=group_id,
        user_id=user_id,
        wallet_address=user.wallet_address or ""
    )
    
    db.add(group)
    db.add(member)
    db.commit()
    db.refresh(group)
    
    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        creator_id=group.creator_id,
        vault_address=group.vault_address,
        created_at=group.created_at,
        member_count=1
    )


@router.get("/", response_model=list[GroupResponse])
async def list_groups(user_id: str, db: Session = Depends(get_db)):
    """List all groups for a user"""
    
    # Get groups where user is a member
    member_records = db.query(GroupMember).filter(GroupMember.user_id == user_id).all()
    group_ids = [m.group_id for m in member_records]
    
    groups = db.query(Group).filter(Group.id.in_(group_ids)).all()
    
    result = []
    for group in groups:
        member_count = db.query(GroupMember).filter(GroupMember.group_id == group.id).count()
        result.append(GroupResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            creator_id=group.creator_id,
            vault_address=group.vault_address,
            created_at=group.created_at,
            member_count=member_count
        ))
    
    return result


@router.get("/{group_id}", response_model=GroupDetailResponse)
async def get_group(group_id: str, user_id: str, db: Session = Depends(get_db)):
    """Get detailed group information"""
    
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
    
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    expense_count = db.query(Expense).filter(Expense.group_id == group_id).count()
    
    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        creator_id=group.creator_id,
        vault_address=group.vault_address,
        created_at=group.created_at,
        member_count=len(members),
        members=[{
            "id": m.id,
            "user_id": m.user_id,
            "wallet_address": m.wallet_address,
            "trust_score": m.trust_score,
            "joined_at": m.joined_at,
            "warning_count": m.warning_count,
            "is_active": m.is_active
        } for m in members],
        expense_count=expense_count
    )


@router.post("/{group_id}/members")
async def add_member(group_id: str, req: AddMemberRequest, user_id: str, db: Session = Depends(get_db)):
    """Add a member to a group"""
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if requester is group creator
    if group.creator_id != user_id:
        raise HTTPException(status_code=403, detail="Only group creator can add members")
    
    new_user = db.query(User).filter(User.id == req.user_id).first()
    if not new_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already member
    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == req.user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User already in group")
    
    member = GroupMember(
        id=str(uuid.uuid4()),
        group_id=group_id,
        user_id=req.user_id,
        wallet_address=new_user.wallet_address or ""
    )
    
    db.add(member)
    db.commit()
    
    return {"message": "Member added", "group_id": group_id, "user_id": req.user_id}


@router.delete("/{group_id}/members/{member_id}")
async def remove_member(group_id: str, member_id: str, user_id: str, db: Session = Depends(get_db)):
    """Remove a member from a group"""
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if requester is group creator
    if group.creator_id != user_id:
        raise HTTPException(status_code=403, detail="Only group creator can remove members")
    
    member = db.query(GroupMember).filter(GroupMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    db.delete(member)
    db.commit()
    
    return {"message": "Member removed"}
