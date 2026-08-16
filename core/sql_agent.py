from __future__ import annotations

import os
import re
import streamlit as st
from groq import Groq


SCHEMA_TEXT = """
Table: claims

Columns:
- claim_id: unique claim identifier
- patient_id: synthetic patient identifier
- claim_date: claim transaction date
- payer: payer organization
- plan: health plan
- drug: therapy/product
- channel: dispensing/distribution channel
- formulary_tier: formulary tier
- prior_auth_required: Yes/No
- step_therapy_required: Yes/No
- quantity_limit: Yes/No
- claim_status: Paid/Rejected
- rejection_reason: reason for rejection or None
- quantity: number of units
- allowed_amount: allowed claim amount
- paid_amount: paid amount

Business rules:
- Rejection rate = rejected claims / total claims.
- Use claim_status = 'Rejected' for rejected claims.
- Segment analysis using payer, plan, drug and channel.
"""


SYSTEM_PROMPT = f"""
You are a healthcare Market Access analytics SQL assistant.

Your task is to convert a user's natural-language analytics question
into ONE safe SQLite SELECT query.

{SCHEMA_TEXT}

Rules:
1. Return ONLY SQL.
2. Only SELECT or WITH...SELECT queries are allowed.
3. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE or PRAGMA.
4. Query only the claims table.
5. Never invent column names.
6. For rejection rate calculate:
   100.0 * rejected_claims / total_claims
7. Use meaningful aliases.
8. Use LIMIT 20 for detail queries unless the user requests another limit.
"""


def get_groq_key():

    try:
        return st.secrets["GROQ_API_KEY"]

    except Exception:

        key = os.getenv("GROQ_API_KEY")

        if not key:
            raise ValueError(
                "GROQ_API_KEY not found. "
                "Check .streamlit/secrets.toml"
            )

        return key


def extract_sql(text: str) -> str:

    text = text.strip()

    text = re.sub(
        r"^```sql\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


def validate_sql(sql: str):

    cleaned = sql.strip().lower()

    if not (
        cleaned.startswith("select")
        or cleaned.startswith("with")
    ):
        return False, "Only SELECT queries are allowed."

    blocked_keywords = [
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "alter ",
        "create ",
        "attach ",
        "pragma ",
        "replace ",
        "vacuum ",
    ]

    for keyword in blocked_keywords:

        if keyword in cleaned:
            return False, f"Unsafe SQL detected: {keyword.strip()}"

    if "claims" not in cleaned:

        return False, "Query must use the claims table."

    return True, ""


def generate_sql(question: str):

    api_key = get_groq_key()

    client = Groq(
        api_key=api_key
    )

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": question
            }

        ],

        temperature=0
    )

    generated_text = response.choices[0].message.content

    sql = extract_sql(generated_text)

    valid, error = validate_sql(sql)

    if not valid:
        raise ValueError(error)

    return sql, "groq"