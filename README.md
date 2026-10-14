# 📊 Market Access AI Analytics Assistant!

An AI-enabled Market Access analytics prototype that combines **LLM-powered natural-language SQL generation** with **SQL and Pandas-based analytics** to analyze the synthetic healthcare claims data.

The application allows users to ask business questions in natural language such as:

> "Which payer has the highest rejection rate?"

The system uses a **Groq LLM** to translate the question into SQL,it validates the generated query and executes it against the claims dataset to return analytical insights.

## LIVE PROJECT LINK : https://market-access-analytics.streamlit.app/
---

## 🚀 Project Overview

Market Access analytics teams work with large datasets involving:

- Payers
- Health plans
- Drugs
- Claims
- Formulary tiers
- Prior authorization
- Step therapy
- Quantity limits
- Rejection reasons
- Distribution channels

This project demonstrates how **AI + traditional analytics** can be combined to make this type of analysis easier and faster.

1. Interactive Market Access dashboard
2. Claims data exploration
3. Natural-language-to-SQL analytics
4. Payer rejection analysis
5. Rejection reason analysis
6. Anomaly detection
7. REST API endpoints
8. Docker containerization
9. GitHub Actions CI

---

# 🏗️ Architecture

```text
                         User
                           |
                           v
                    Streamlit UI
                           |
             Natural-Language Question
                           |
                           v
                      Groq LLM
                  Llama 3.3 70B
                           |
                           v
                    Generated SQL
                           |
                           v
                    SQL Validation
                           |
                           v
                SQLite / Claims Data
                           |
                    +------+------+
                    |             |
                    v             v
                   SQL         Pandas
                    |             |
                    +------+------+
                           |
                           v
                    Analytics Result
                           |
                           v
                         User

---

# REST API Architecture

                  Client / Application
                           |
                           v
                       Flask API
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
       /health           /ask           /report/*
          |                |                |
          |                v                |
          |             Groq LLM            |
          |                |                |
          +----------------+----------------+
                           |
                           v
                  SQL / Pandas Analytics
                           |
                           v
                     Claims Dataset
