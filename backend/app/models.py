from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    AGENT = "AGENT"
    INVESTIGATOR = "INVESTIGATOR"


class ClaimStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    AUTO_APPROVED = "AUTO_APPROVED"
    INVESTIGATION = "INVESTIGATION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PAID = "PAID"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default=UserRole.AGENT.value)
    full_name: Mapped[str] = mapped_column(String(120))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    claims: Mapped[list["Claim"]] = relationship(back_populates="created_by")


class Policy(Base):
    __tablename__ = "policies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    policy_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(120))
    policy_type: Mapped[str] = mapped_column(String(40))
    location: Mapped[str] = mapped_column(String(80))
    start_date: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    claims: Mapped[list["Claim"]] = relationship(back_populates="policy")


class Claim(Base):
    __tablename__ = "claims"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    policy_id: Mapped[int] = mapped_column(ForeignKey("policies.id"))
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    claim_type: Mapped[str] = mapped_column(String(40))
    claim_amount: Mapped[float] = mapped_column(Float)
    previous_claims: Mapped[int] = mapped_column(Integer, default=0)
    claim_frequency_30d: Mapped[int] = mapped_column(Integer, default=0)
    location_risk: Mapped[float] = mapped_column(Float, default=0.2)
    mismatch_score: Mapped[float] = mapped_column(Float, default=0.1)
    late_report_days: Mapped[int] = mapped_column(Integer, default=0)
    weekend_claim: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(30), default=ClaimStatus.SUBMITTED.value)
    fraud_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    anomaly_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    policy: Mapped[Policy] = relationship(back_populates="claims")
    created_by: Mapped[User] = relationship(back_populates="claims")
    audits: Mapped[list["AuditLog"]] = relationship(back_populates="claim", cascade="all, delete-orphan")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id: Mapped[int | None] = mapped_column(ForeignKey("claims.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(80))
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    claim: Mapped[Claim | None] = relationship(back_populates="audits")
