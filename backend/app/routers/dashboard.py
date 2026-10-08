from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from ..db import get_db
from ..models import Claim, User
from ..security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = db.query(func.count(Claim.id)).scalar() or 0
    high = db.query(func.count(Claim.id)).filter(Claim.risk_level == "HIGH").scalar() or 0
    investigation = db.query(func.count(Claim.id)).filter(Claim.status == "INVESTIGATION").scalar() or 0
    approved = db.query(func.count(Claim.id)).filter(Claim.status.in_(["APPROVED", "AUTO_APPROVED", "PAID"])).scalar() or 0
    avg_risk = db.query(func.avg(Claim.risk_score)).scalar() or 0
    total_amount = db.query(func.sum(Claim.claim_amount)).scalar() or 0
    return {
        "total_claims": total,
        "high_risk_claims": high,
        "investigations": investigation,
        "approved_claims": approved,
        "average_risk_score": round(float(avg_risk), 2),
        "total_claim_amount": round(float(total_amount), 2),
    }


@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(Claim.risk_level, func.count(Claim.id)).group_by(Claim.risk_level).all()
    return [{"risk_level": r or "UNSCORED", "count": c} for r, c in rows]
