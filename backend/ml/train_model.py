from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from xgboost import XGBClassifier

BASE = Path(__file__).resolve().parent
ARTIFACTS = BASE / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)
DATASET = BASE.parent / "data" / "synthetic_claims.csv"

FEATURES = [
    "claim_amount",
    "previous_claims",
    "claim_frequency_30d",
    "location_risk",
    "mismatch_score",
    "late_report_days",
    "weekend_claim",
]


def generate_dataset(n: int = 8000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    claim_amount = np.clip(rng.gamma(shape=2.4, scale=12000, size=n), 500, 250000)
    previous_claims = rng.poisson(lam=1.4, size=n).clip(0, 15)
    claim_frequency = rng.poisson(lam=0.8, size=n).clip(0, 10)
    location_risk = rng.beta(2, 5, size=n)
    mismatch = rng.beta(1.5, 6, size=n)
    late_days = rng.exponential(scale=2.4, size=n).clip(0, 60).round().astype(int)
    weekend = rng.binomial(1, 0.29, size=n)

    logit = (
        -5.0
        + 0.000018 * claim_amount
        + 0.22 * previous_claims
        + 0.38 * claim_frequency
        + 2.6 * location_risk
        + 3.1 * mismatch
        + 0.045 * late_days
        + 0.30 * weekend
    )
    probability = 1 / (1 + np.exp(-logit))
    fraud = rng.binomial(1, probability)

    df = pd.DataFrame({
        "claim_amount": claim_amount.round(2),
        "previous_claims": previous_claims,
        "claim_frequency_30d": claim_frequency,
        "location_risk": location_risk.round(4),
        "mismatch_score": mismatch.round(4),
        "late_report_days": late_days,
        "weekend_claim": weekend,
        "fraud": fraud,
    })
    return df


def main():
    df = generate_dataset()
    DATASET.parent.mkdir(exist_ok=True)
    df.to_csv(DATASET, index=False)

    X = df[FEATURES]
    y = df["fraud"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    rf = RandomForestClassifier(
        n_estimators=320,
        max_depth=12,
        min_samples_leaf=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)

    positive_weight = float((y_train == 0).sum() / max((y_train == 1).sum(), 1))
    xgb = XGBClassifier(
        n_estimators=260,
        max_depth=6,
        learning_rate=0.06,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="binary:logistic",
        eval_metric="logloss",
        scale_pos_weight=positive_weight,
        random_state=42,
        n_jobs=4,
    )
    xgb.fit(X_train, y_train)

    rf_auc = roc_auc_score(y_test, rf.predict_proba(X_test)[:, 1])
    xgb_auc = roc_auc_score(y_test, xgb.predict_proba(X_test)[:, 1])
    classifier = xgb if xgb_auc >= rf_auc else rf
    model_name = "XGBoost" if xgb_auc >= rf_auc else "Random Forest"

    anomaly = IsolationForest(
        n_estimators=250,
        contamination=0.08,
        random_state=42,
    )
    anomaly.fit(X_train)

    train_decisions = -anomaly.decision_function(X_train)
    bundle = {
        "classifier": classifier,
        "model_name": model_name,
        "random_forest_auc": float(rf_auc),
        "xgboost_auc": float(xgb_auc),
        "anomaly": anomaly,
        "anomaly_min": float(train_decisions.min()),
        "anomaly_max": float(train_decisions.max()),
        "baselines": {f: float(X_train[f].median()) for f in FEATURES},
        "features": FEATURES,
    }
    path = ARTIFACTS / "model_bundle.joblib"
    joblib.dump(bundle, path)

    pred = classifier.predict_proba(X_test)[:, 1]
    print("Random Forest ROC-AUC:", round(rf_auc, 4))
    print("XGBoost ROC-AUC:", round(xgb_auc, 4))
    print("Selected model:", model_name)
    print("Selected ROC-AUC:", round(roc_auc_score(y_test, pred), 4))
    print(classification_report(y_test, (pred >= 0.5).astype(int)))
    print("Saved:", path)


if __name__ == "__main__":
    main()
