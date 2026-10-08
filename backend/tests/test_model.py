from app.services.ml_service import ml_service


def test_model_scores_claim():
    result = ml_service.score({
        'claim_amount': 50000,
        'previous_claims': 4,
        'claim_frequency_30d': 3,
        'location_risk': .65,
        'mismatch_score': .55,
        'late_report_days': 10,
        'weekend_claim': True,
    })
    assert 0 <= result['fraud_probability'] <= 1
    assert 0 <= result['anomaly_score'] <= 1
    assert 0 <= result['risk_score'] <= 100
    assert result['risk_level'] in {'LOW', 'MEDIUM', 'HIGH'}
    assert result['factors']
