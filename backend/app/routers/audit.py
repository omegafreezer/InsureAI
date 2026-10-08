from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import AuditLog, User
from ..security import get_current_user, require_roles

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("")
def audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "INVESTIGATOR")),
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [
        {
            "id": x.id,
            "claim_id": x.claim_id,
            "user_id": x.user_id,
            "action": x.action,
            "details": x.details,
            "created_at": x.created_at,
        }
        for x in logs
    ]
