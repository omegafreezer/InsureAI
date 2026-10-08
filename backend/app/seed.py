from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import User, Policy, Claim, AuditLog, ClaimStatus
from .security import hash_password


def seed_database():
    db: Session = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add_all([
                User(username="admin", password_hash=hash_password("Admin@123"), role="ADMIN", full_name="System Administrator"),
                User(username="agent", password_hash=hash_password("Agent@123"), role="AGENT", full_name="Claims Agent"),
                User(username="investigator", password_hash=hash_password("Invest@123"), role="INVESTIGATOR", full_name="Fraud Investigator"),
            ])
            db.commit()

        if db.query(Policy).count() == 0:
            policies = [
                Policy(policy_number="POL-10001", customer_name="Aarav Mehta", policy_type="AUTO", location="Bengaluru", start_date=datetime.utcnow()-timedelta(days=420)),
                Policy(policy_number="POL-10002", customer_name="Priya Sharma", policy_type="HOME", location="Pune", start_date=datetime.utcnow()-timedelta(days=270)),
                Policy(policy_number="POL-10003", customer_name="Rohan Singh", policy_type="PROPERTY", location="Hyderabad", start_date=datetime.utcnow()-timedelta(days=95)),
            ]
            db.add_all(policies)
            db.commit()

            agent = db.query(User).filter(User.username == "agent").first()
            policies_by_number = {p.policy_number: p for p in db.query(Policy).all()}
            demo_claims = [
                Claim(claim_number="CLM-DEMO-001", policy_id=policies_by_number["POL-10001"].id, created_by_id=agent.id, claim_type="COLLISION", claim_amount=7200, previous_claims=1, claim_frequency_30d=1, location_risk=.12, mismatch_score=.08, late_report_days=1, weekend_claim=False, status="AUTO_APPROVED", fraud_probability=.09, anomaly_score=.10, risk_score=9.3, risk_level="LOW", decision_reason="Low-risk claim automatically approved by the decision engine."),
                Claim(claim_number="CLM-DEMO-002", policy_id=policies_by_number["POL-10002"].id, created_by_id=agent.id, claim_type="WATER_DAMAGE", claim_amount=48000, previous_claims=4, claim_frequency_30d=3, location_risk=.58, mismatch_score=.42, late_report_days=8, weekend_claim=True, status="INVESTIGATION", fraud_probability=.74, anomaly_score=.68, risk_score=72.2, risk_level="HIGH", decision_reason="High-risk claim routed for manual investigation."),
                Claim(claim_number="CLM-DEMO-003", policy_id=policies_by_number["POL-10003"].id, created_by_id=agent.id, claim_type="FIRE", claim_amount=18500, previous_claims=2, claim_frequency_30d=1, location_risk=.36, mismatch_score=.22, late_report_days=4, weekend_claim=False, status="SUBMITTED", fraud_probability=.41, anomaly_score=.38, risk_score=40.1, risk_level="MEDIUM", decision_reason="Medium-risk claim requires reviewer assessment."),
            ]
            db.add_all(demo_claims)
            db.commit()
    finally:
        db.close()
