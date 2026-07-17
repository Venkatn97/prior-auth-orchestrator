import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Text, Enum, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


def utcnow():
    return datetime.now(timezone.utc)


class RequestStatus(str, enum.Enum):
    intake = "intake"
    in_review = "in_review"
    pending_approval = "pending_approval"
    approved = "approved"
    denied = "denied"
    closed = "closed"


class Request(Base):
    __tablename__ = "requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_ref = Column(String, nullable=False)
    status = Column(Enum(RequestStatus), nullable=False, default=RequestStatus.intake)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    decisions = relationship("AgentDecision", back_populates="request")
    approvals = relationship("Approval", back_populates="request")


class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("requests.id"), nullable=False)
    cluster = Column(String, nullable=False)
    agent_name = Column(String, nullable=False)
    decision = Column(JSON, nullable=False)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    request = relationship("Request", back_populates="decisions")


class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("requests.id"), nullable=False)
    status = Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.pending)
    reason = Column(Text, nullable=True)
    reviewed_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    request = relationship("Request", back_populates="approvals")