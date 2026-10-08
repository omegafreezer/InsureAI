from pathlib import Path
import numpy as np
import pandas as pd
import joblib

MODEL_PATH = Path(__file__).resolve().parents[2] / "ml" / "artifacts" / "model_bundle.joblib"

FEATURES = [
    "claim_amount",
    "previous_claims",
    "claim_frequency_30d",
    "location_risk",
    "mismatch_score",
    "late_report_days",
    "weekend_claim",
]


class MLService:
    def __init__(self):
        self.bundle = None
        self.load()

    def load(self):
        if MODEL_PATH.exists():
            self.bundle = joblib.load(MODEL_PATH)

    def ensure_model(self):
        if self.bundle is None:
            raise RuntimeError("ML model not found. Run: python -m ml.train_model")

    def _frame(self, payload: dict) -> pd.DataFrame:
        row = {f: payload[f] for f in FEATURES}
        row["weekend_claim"] = int(bool(row["weekend_claim"]))
        return pd.DataFrame([row], columns=FEATURES)

    def score(self, payload: dict) -> dict:
        self.ensure_model()
        frame = self._frame(payload)
        classifier = self.bundle["classifier"]
        anomaly = self.bundle["anomaly"]
        probability = float(classifier.predict_proba(frame)[0, 1])
        decision = float(anomaly.decision_function(frame)[0])
        raw_anomaly = float(-decision)
        # Calibrate anomaly contribution into an interpretable 0-1 range using training reference bounds.
        a_min = self.bundle["anomaly_min"]
        a_max = self.bundle["anomaly_max"]
        anomaly_norm = float(np.clip((raw_anomaly - a_min) / (a_max - a_min + 1e-9), 0, 1))
        risk_score = round((0.70 * probability + 0.30 * anomaly_norm) * 100, 2)
        level = "LOW" if risk_score < 35 else "MEDIUM" if risk_score < 65 else "HIGH"
        factors = self.explain(payload, probability, anomaly_norm)
        return {
            "fraud_probability": round(probability, 4),
            "anomaly_score": round(anomaly_norm, 4),
            "risk_score": risk_score,
            "risk_level": level,
            "factors": factors,
        }

    def explain(self, payload: dict, probability: float, anomaly_norm: float) -> list[dict]:
        values = {
            "claim_amount": float(payload["claim_amount"]),
            "previous_claims": float(payload["previous_claims"]),
            "claim_frequency_30d": float(payload["claim_frequency_30d"]),
            "location_risk": float(payload["location_risk"]),
            "mismatch_score": float(payload["mismatch_score"]),
            "late_report_days": float(payload["late_report_days"]),
            "weekend_claim": float(bool(payload["weekend_claim"])),
        }
        baselines = self.bundle["baselines"]
        labels = {
            "claim_amount": "Claim amount",
            "previous_claims": "Previous claims",
            "claim_frequency_30d": "30-day claim frequency",
            "location_risk": "Location risk",
            "mismatch_score": "Policy/claim mismatch",
            "late_report_days": "Late reporting days",
            "weekend_claim": "Weekend claim",
        }
        impacts = []
        for key, value in values.items():
            base = baselines[key]
            ratio = value / (base + 1e-9)
            if key in {"location_risk", "mismatch_score"}:
                contribution = value
            elif key == "weekend_claim":
                contribution = 0.10 if value else 0.0
            else:
                contribution = np.clip((ratio - 1) / 2, -0.5, 1.0)
            impacts.append((key, float(contribution)))
        impacts.sort(key=lambda item: abs(item[1]), reverse=True)
        result = []
        for key, contribution in impacts[:5]:
            direction = "increases" if contribution > 0.08 else "decreases" if contribution < -0.08 else "neutral"
            result.append({
                "feature": labels[key],
                "impact": round(contribution, 3),
                "direction": direction,
                "message": f"{labels[key]} {direction} fraud risk relative to the baseline."
            })
        result.append({
            "feature": "Model confidence",
            "impact": round(probability, 3),
            "direction": "high-risk" if probability >= 0.65 else "moderate" if probability >= 0.35 else "low-risk",
            "message": f"Supervised fraud probability: {probability:.1%}."
        })
        return result


ml_service = MLService()
