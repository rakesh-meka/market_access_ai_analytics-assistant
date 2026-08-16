import pandas as pd
from core.analytics import rejection_rate, payer_rejection_summary, execute_sql


def sample_df():
    return pd.DataFrame({
        "claim_id": ["1", "2", "3"],
        "payer": ["A", "A", "B"],
        "claim_status": ["Paid", "Rejected", "Rejected"],
        "drug": ["X", "X", "Y"],
        "claim_date": pd.to_datetime(["2026-01-01", "2026-01-01", "2026-01-02"]),
        "paid_amount": [100.0, 0.0, 0.0],
    })


def test_rejection_rate():
    assert rejection_rate(sample_df()) == 66.67


def test_payer_summary():
    out = payer_rejection_summary(sample_df())
    assert out.iloc[0]["payer"] == "B"


def test_execute_sql():
    result = execute_sql(
        sample_df(),
        "SELECT payer, COUNT(*) AS claims FROM claims GROUP BY payer ORDER BY claims DESC"
    )
    assert list(result["payer"]) == ["A", "B"]
