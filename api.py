from flask import Flask, jsonify, request
from core.analytics import load_claims, execute_sql
from core.sql_agent import generate_sql

app = Flask(__name__)
df = load_claims("data/claims.csv")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/ask")
def ask():
    payload = request.get_json(silent=True) or {}
    question = payload.get("question", "").strip()

    if not question:
        return jsonify({"error": "question is required"}), 400

    try:
        sql, mode = generate_sql(question)
        result = execute_sql(df, sql)

        return jsonify({
            "question": question,
            "mode": mode,
            "sql": sql,
            "result": result.to_dict(orient="records"),
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
