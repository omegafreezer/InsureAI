from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    model_config = ConfigDict(from_attributes=True)


class ClaimCreate(BaseModel):
    policy_number: str
    customer_name: str = Field(min_length=2, max_length=120)
    policy_type: str
    location: str
    claim_type: str
    claim_amount: float = Field(gt=0)
    previous_claims: int = Field(ge=0, le=100)
    claim_frequency_30d: int = Field(ge=0, le=100)
    location_risk: float = Field(ge=0, le=1)
    mismatch_score: float = Field(ge=0, le=1)
    late_report_days: int = Field(ge=0, le=365)
    weekend_claim: bool = False


class ClaimDecision(BaseModel):
    decision: str
    note: Optional[str] = Field(default=None, max_length=500)


class ClaimOut(BaseModel):
    id: int
    claim_number: str
    policy_number: str
    customer_name: str
    policy_type: str
    claim_type: str
    claim_amount: float
    location: str
    status: str
    fraud_probability: Optional[float]
    anomaly_score: Optional[float]
    risk_score: Optional[float]
    risk_level: Optional[str]
    decision_reason: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RiskExplanation(BaseModel):
    claim_number: str
    risk_score: float
    risk_level: str
    factors: list[dict]
