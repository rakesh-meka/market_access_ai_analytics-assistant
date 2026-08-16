from __future__ import annotations

import pandas as pd
import sqlite3


def load_claims(path: str = "data/claims.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["claim_date"])
    return df


def get_connection(df: pd.DataFrame) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df.to_sql("claims", conn, index=False, if_exists="replace")
    return conn


def rejection_rate(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    return round((df["claim_status"].eq("Rejected").mean()) * 100, 2)


def payer_rejection_summary(df: pd.DataFrame) -> pd.DataFrame:
    result = (
        df.groupby("payer", as_index=False)
          .agg(
              total_claims=("claim_id", "count"),
              rejected_claims=("claim_status", lambda s: (s == "Rejected").sum()),
              paid_claims=("claim_status", lambda s: (s == "Paid").sum()),
          )
    )
    result["rejection_rate_pct"] = (
        result["rejected_claims"] / result["total_claims"] * 100
    ).round(2)
    return result.sort_values("rejection_rate_pct", ascending=False)


def rejection_reason_summary(df: pd.DataFrame, payer: str | None = None) -> pd.DataFrame:
    work = df.copy()
    if payer:
        work = work[work["payer"] == payer]
    work = work[work["claim_status"] == "Rejected"]
    result = (
        work.groupby("rejection_reason", as_index=False)
            .size()
            .rename(columns={"size": "rejected_claims"})
            .sort_values("rejected_claims", ascending=False)
    )
    return result


def daily_rejection_rate(df: pd.DataFrame) -> pd.DataFrame:
    result = (
        df.assign(
            rejected=(df["claim_status"] == "Rejected").astype(int)
        )
        .groupby("claim_date", as_index=False)
        .agg(
            claims=("claim_id", "count"),
            rejected_claims=("rejected", "sum"),
        )
    )
    result["rejection_rate_pct"] = (
        result["rejected_claims"] / result["claims"] * 100
    ).round(2)
    return result.sort_values("claim_date")


def detect_daily_anomalies(df: pd.DataFrame, z_threshold: float = 2.0) -> pd.DataFrame:
    daily = daily_rejection_rate(df)
    if daily.empty or daily["rejection_rate_pct"].std(ddof=0) == 0:
        daily["z_score"] = 0.0
        daily["is_anomaly"] = False
        return daily

    mean = daily["rejection_rate_pct"].mean()
    std = daily["rejection_rate_pct"].std(ddof=0)
    daily["z_score"] = ((daily["rejection_rate_pct"] - mean) / std).round(2)
    daily["is_anomaly"] = daily["z_score"].abs() >= z_threshold
    return daily.sort_values("claim_date")


def execute_sql(df: pd.DataFrame, sql: str) -> pd.DataFrame:
    conn = get_connection(df)
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()
