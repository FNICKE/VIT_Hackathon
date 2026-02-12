from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    wallet_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    groups = relationship("Group", back_populates="creator")
    group_members = relationship("GroupMember", back_populates="user")
    expenses = relationship("Expense", back_populates="paid_by_user")


class Group(Base):
    __tablename__ = "groups"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    vault_address = Column(String, nullable=True)  # Algorand escrow address
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = relationship("User", back_populates="groups")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="group", cascade="all, delete-orphan")
    settlements = relationship("Settlement", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, ForeignKey("groups.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    wallet_address = Column(String, nullable=True)
    trust_score = Column(Float, default=0.5)
    joined_at = Column(DateTime, default=datetime.utcnow)
    warning_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_members")


class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, ForeignKey("groups.id"), nullable=False, index=True)
    paid_by_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    settled = Column(Boolean, default=False)
    
    group = relationship("Group", back_populates="expenses")
    paid_by_user = relationship("User", back_populates="expenses")


class Settlement(Base):
    __tablename__ = "settlements"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, ForeignKey("groups.id"), nullable=False, index=True)
    
    # Settlement data from LangGraph
    settlements = Column(JSON, default={})  # List of {from, to, amount}
    risk_scores = Column(JSON, default={})  # {user_id: score}
    warnings = Column(JSON, default={})  # {user_id: level}
    excluded_members = Column(JSON, default=[])  # [user_ids]
    governance_actions = Column(JSON, default={})  # Enforcement decisions
    onchain_results = Column(JSON, default={})  # Blockchain execution results
    explanation = Column(String, nullable=True)  # LLM explanation
    
    # Blockchain execution details
    txn_hash = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, executed, failed, confirmed
    
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    
    group = relationship("Group", back_populates="settlements")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)  # User, Group, Settlement, etc
    entity_id = Column(String, nullable=False)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
