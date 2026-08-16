from __future__ import annotations

import streamlit as st
import pandas as pd

from core.analytics import (
    load_claims,
    rejection_rate,
    payer_rejection_summary,
    rejection_reason_summary,
    detect_daily_anomalies,
    execute_sql,
)

from core.sql_agent import generate_sql


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Market Access AI Analytics Assistant",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("📊 Market Access AI Analytics Assistant")

st.caption(
    "AI-powered analytics for synthetic healthcare claims data "
    "covering payer, plan, formulary and access insights."
)

st.info(
    "Educational demo only. The claims dataset is synthetic and does not "
    "represent real patients, real payers or real healthcare transactions."
)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data
def load_data():

    return load_claims("data/claims.csv")


df = load_data()


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------

st.sidebar.header("🔎 Filters")

selected_payer = st.sidebar.multiselect(
    "Payer",
    sorted(df["payer"].unique()),
    default=[],
)

selected_drug = st.sidebar.multiselect(
    "Drug",
    sorted(df["drug"].unique()),
    default=[],
)

selected_channel = st.sidebar.multiselect(
    "Channel",
    sorted(df["channel"].unique()),
    default=[],
)


# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------

filtered = df.copy()


if selected_payer:

    filtered = filtered[
        filtered["payer"].isin(selected_payer)
    ]


if selected_drug:

    filtered = filtered[
        filtered["drug"].isin(selected_drug)
    ]


if selected_channel:

    filtered = filtered[
        filtered["channel"].isin(selected_channel)
    ]


# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Overview",
        "📋 Claims Explorer",
        "🤖 Natural-Language SQL",
        "🚨 Anomaly Detection",
    ]
)


# =========================================================
# TAB 1 — OVERVIEW
# =========================================================

with tab1:

    st.header("Market Access Claims Overview")

    # KPI cards

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Claims",
        f"{len(filtered):,}",
    )

    c2.metric(
        "Rejection Rate",
        f"{rejection_rate(filtered):.2f}%",
    )

    c3.metric(
        "Payers",
        filtered["payer"].nunique(),
    )

    c4.metric(
        "Paid Amount",
        f"${filtered['paid_amount'].sum():,.0f}",
    )


    # -----------------------------------------------------
    # Rejection Rate by Payer
    # -----------------------------------------------------

    st.subheader("Rejection Rate by Payer")

    payer_summary = payer_rejection_summary(filtered)

    st.dataframe(
        payer_summary,
        use_container_width=True,
        hide_index=True,
    )

    if not payer_summary.empty:

        st.bar_chart(
            payer_summary.set_index("payer")[
                "rejection_rate_pct"
            ]
        )


    # -----------------------------------------------------
    # Rejection Reasons
    # -----------------------------------------------------

    st.subheader("Top Rejection Reasons")

    reason_summary = rejection_reason_summary(
        filtered
    )

    st.dataframe(
        reason_summary,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# TAB 2 — CLAIMS EXPLORER
# =========================================================

with tab2:

    st.header("Claims Explorer")

    st.write(
        f"Showing the latest claims from "
        f"{len(filtered):,} filtered records."
    )

    st.dataframe(
        filtered.sort_values(
            "claim_date",
            ascending=False,
        ).head(300),
        use_container_width=True,
        hide_index=True,
    )


    # Download filtered data

    st.download_button(
        label="⬇️ Download Filtered Claims",
        data=filtered.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="filtered_claims.csv",
        mime="text/csv",
    )


# =========================================================
# TAB 3 — NATURAL LANGUAGE SQL
# =========================================================

with tab3:

    st.header(
        "🤖 Ask a Market Access Analytics Question"
    )

    st.write(
        "Ask a question in normal English. "
        "The Groq LLM will translate your question into SQL "
        "and the application will execute the SQL against the claims data."
    )


    # -----------------------------------------------------
    # Example Questions
    # -----------------------------------------------------

    st.subheader("Example Questions")

    examples = [
        "Which payer has the highest rejection rate?",
        "What is the rejection rate by payer?",
        "What are the main rejection reasons?",
        "Which channel has the highest rejection rate?",
        "How many total claims are in the dataset?",
        "What is the total paid amount?",
    ]

    st.code(
        "\n".join(examples),
        language="text",
    )


    # -----------------------------------------------------
    # User Question
    # -----------------------------------------------------

    question = st.text_input(
        "Enter your question",
        placeholder=(
            "Example: Which payer has the highest rejection rate?"
        ),
    )


    # -----------------------------------------------------
    # RUN BUTTON
    # -----------------------------------------------------

    if st.button(
        "🚀 Run Analytics",
        type="primary",
    ) and question:

        try:

            # ---------------------------------------------
            # Generate SQL using Groq
            # ---------------------------------------------

            with st.spinner(
                "🤖 Groq is understanding your question "
                "and generating SQL..."
            ):

                sql, mode = generate_sql(
                    question
                )


            # ---------------------------------------------
            # LLM Status
            # ---------------------------------------------

            if mode == "groq":

                st.success(
                    "✅ Groq LLM successfully generated the SQL."
                )

            else:

                st.info(
                    f"LLM Provider: {mode}"
                )


            # ---------------------------------------------
            # Show Generated SQL
            # ---------------------------------------------

            st.subheader(
                "🧠 Generated SQL"
            )

            st.code(
                sql,
                language="sql",
            )


            # ---------------------------------------------
            # Execute SQL
            # ---------------------------------------------

            with st.spinner(
                "Running SQL against claims data..."
            ):

                result = execute_sql(
                    filtered,
                    sql,
                )


            # ---------------------------------------------
            # Display Result
            # ---------------------------------------------

            st.subheader(
                "📊 Analytics Result"
            )

            if result.empty:

                st.warning(
                    "The query returned no results."
                )

            else:

                st.dataframe(
                    result,
                    use_container_width=True,
                    hide_index=True,
                )


                # -----------------------------------------
                # Visualization
                # -----------------------------------------

                if len(result.columns) >= 2:

                    try:

                        st.subheader(
                            "📈 Visualization"
                        )

                        chart_data = result.set_index(
                            result.columns[0]
                        )

                        st.bar_chart(
                            chart_data
                        )

                    except Exception:

                        pass


        except Exception as exc:

            st.error(
                f"❌ Unable to run the question: {exc}"
            )

            st.info(
                "Check that your Groq API key is correctly "
                "configured in .streamlit/secrets.toml "
                "and that core/sql_agent.py is using the "
                "Groq Chat Completions API."
            )


# =========================================================
# TAB 4 — ANOMALY DETECTION
# =========================================================

with tab4:

    st.header(
        "🚨 Daily Rejection-Rate Anomaly Detection"
    )

    st.write(
        "This section identifies unusual daily rejection-rate "
        "patterns using a simple z-score approach."
    )


    # -----------------------------------------------------
    # Detect anomalies
    # -----------------------------------------------------

    anomalies = detect_daily_anomalies(
        filtered
    )


    flagged = anomalies[
        anomalies["is_anomaly"]
    ]


    # -----------------------------------------------------
    # KPI cards
    # -----------------------------------------------------

    c1, c2 = st.columns(2)

    c1.metric(
        "Days Analyzed",
        len(anomalies),
    )

    c2.metric(
        "Anomalous Days",
        len(flagged),
    )


    # -----------------------------------------------------
    # Trend chart
    # -----------------------------------------------------

    st.subheader(
        "Daily Rejection Rate Trend"
    )

    if not anomalies.empty:

        st.line_chart(
            anomalies.set_index(
                "claim_date"
            )[
                "rejection_rate_pct"
            ]
        )


    # -----------------------------------------------------
    # Flagged anomalies
    # -----------------------------------------------------

    st.subheader(
        "Flagged Anomalies"
    )

    if flagged.empty:

        st.success(
            "No significant anomalies were detected."
        )

    else:

        st.dataframe(
            flagged.sort_values(
                "z_score",
                key=lambda s: s.abs(),
                ascending=False,
            ),
            use_container_width=True,
            hide_index=True,
        )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Architecture: Streamlit → Groq LLM → SQL Validation "
    "→ SQL/Pandas Analytics → Market Access Insights"
)