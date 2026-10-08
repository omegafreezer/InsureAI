from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from ..config import get_settings
from ..db import get_db
from ..models import AuditLog, Claim, ClaimStatus, Policy, User
from ..schemas import ClaimCreate, ClaimDecision, ClaimOut, RiskExplanation
from ..security import get_current_user, require_roles
from ..services.ml_service import ml_service

router = APIRouter(prefix="/claims", tags=["Claims"])
settings = get_settings()


def claim_to_out(claim: Claim) -> dict:
    return {
        "id": claim.id,
        "claim_number": claim.claim_number,
        "policy_number": claim.policy.policy_number,
        "customer_name": claim.policy.customer_name,
        "policy_type": claim.policy.policy_type,
        "claim_type": claim.claim_type,
        "claim_amount": claim.claim_amount,
        "location": claim.policy.location,
        "status": claim.status,
        "fraud_probability": claim.fraud_probability,
        "anomaly_score": claim.anomaly_score,
        "risk_score": claim.risk_score,
        "risk_level": claim.risk_level,
        "decision_reason": claim.decision_reason,
        "created_at": claim.created_at,
    }


@router.post("", response_model=ClaimOut)
def create_claim(
    payload: ClaimCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "AGENT")),
):
    policy = db.query(Policy).filter(Policy.policy_number == payload.policy_number).first()
    if not policy:
        policy = Policy(
            policy_number=payload.policy_number,
            customer_name=payload.customer_name,
            policy_type=payload.policy_type,
            location=payload.location,
            start_date=datetime.utcnow() - timedelta(days=180),
        )
        db.add(policy)
        db.flush()

    claim_number = f"CLM-{datetime.utcnow():%Y%m%d}-{uuid4().hex[:6].upper()}"
    claim = Claim(
        claim_number=claim_number,
        policy_id=policy.id,
        created_by_id=current_user.id,
        claim_type=payload.claim_type,
        claim_amount=payload.claim_amount,
        previous_claims=payload.previous_claims,
        claim_frequency_30d=payload.claim_frequency_30d,
        location_risk=payload.location_risk,
        mismatch_score=payload.mismatch_score,
        late_report_days=payload.late_report_days,
        weekend_claim=payload.weekend_claim,
    )
    db.add(claim)
    db.flush()
    scored = ml_service.score(payload.model_dump())
    claim.fraud_probability = scored["fraud_probability"]
    claim.anomaly_score = scored["anomaly_score"]
    claim.risk_score = scored["risk_score"]
    claim.risk_level = scored["risk_level"]
    if claim.risk_score < settings.auto_approval_threshold:
        claim.status = ClaimStatus.AUTO_APPROVED.value
        claim.decision_reason = "Low-risk claim automatically approved by the decision engine."
    elif claim.risk_score >= settings.investigation_threshold:
        claim.status = ClaimStatus.INVESTIGATION.value
        claim.decision_reason = "High-risk claim routed for manual investigation."
    else:
        claim.status = ClaimStatus.SUBMITTED.value
        claim.decision_reason = "Medium-risk claim requires reviewer assessment."

    db.add(AuditLog(claim_id=claim.id, user_id=current_user.id, action="CLAIM_CREATED", details=claim.decision_reason))
    db.commit()
    db.refresh(claim)
    return claim_to_out(claim)


@router.get("", response_model=list[ClaimOut])
def list_claims(
    status_filter: str | None = Query(default=None, alias="status"),
    risk: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Claim).options(joinedload(Claim.policy)).order_by(Claim.created_at.desc())
    if status_filter:
        q = q.filter(Claim.status == status_filter)
    if risk:
        q = q.filter(Claim.risk_level == risk.upper())
    return [claim_to_out(c) for c in q.all()]


@router.get("/{claim_id}", response_model=ClaimOut)
def get_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    claim = db.query(Claim).options(joinedload(Claim.policy)).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim_to_out(claim)


@router.post("/{claim_id}/rescore", response_model=RiskExplanation)
def rescore_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "AGENT", "INVESTIGATOR")),
):
    claim = db.query(Claim).options(joinedload(Claim.policy)).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    payload = {
        "claim_amount": claim.claim_amount,
        "previous_claims": claim.previous_claims,
        "claim_frequency_30d": claim.claim_frequency_30d,
        "location_risk": claim.location_risk,
        "mismatch_score": claim.mismatch_score,
        "late_report_days": claim.late_report_days,
        "weekend_claim": claim.weekend_claim,
    }
    scored = ml_service.score(payload)
    claim.fraud_probability = scored["fraud_probability"]
    claim.anomaly_score = scored["anomaly_score"]
    claim.risk_score = scored["risk_score"]
    claim.risk_level = scored["risk_level"]
    db.add(AuditLog(claim_id=claim.id, user_id=current_user.id, action="RESCORED", details=f"Risk score {claim.risk_score}"))
    db.commit()
    return RiskExplanation(
        claim_number=claim.claim_number,
        risk_score=claim.risk_score,
        risk_level=claim.risk_level,
        factors=scored["factors"],
    )


@router.post("/{claim_id}/decision", response_model=ClaimOut)
def decide_claim(
    claim_id: int,
    payload: ClaimDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "INVESTIGATOR")),
):
    decision = payload.decision.upper()
    if decision not in {"APPROVE", "REJECT", "PAID"}:
        raise HTTPException(status_code=400, detail="Decision must be APPROVE, REJECT or PAID")
    claim = db.query(Claim).options(joinedload(Claim.policy)).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    mapping = {"APPROVE": ClaimStatus.APPROVED.value, "REJECT": ClaimStatus.REJECTED.value, "PAID": ClaimStatus.PAID.value}
    claim.status = mapping[decision]
    claim.decision_reason = payload.note or f"{decision.title()}d by {current_user.full_name}."
    db.add(AuditLog(claim_id=claim.id, user_id=current_user.id, action=f"DECISION_{decision}", details=claim.decision_reason))
    db.commit()
    db.refresh(claim)
    return claim_to_out(claim)
