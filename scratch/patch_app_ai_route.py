with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

def normalize(s):
    return s.replace("\r\n", "\n")

text_norm = normalize(text)

route_code = """@app.route("/api/calculators/ai-insight", methods=["POST"])
def calculator_ai_insight():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    payload = request.get_json(silent=True) or {}
    module = str(payload.get("module", "feeding")).strip().lower()
    data = payload.get("data") or {}

    try:
        from calculator_ai_service import get_calculator_ai_insight
        result = get_calculator_ai_insight(module, data)
        return jsonify(result)
    except Exception as exc:
        app.logger.exception("Error generating calculator AI insight: %s", exc)
        return jsonify({"error": "Failed to generate AI evaluation.", "details": str(exc)}), 500


if __name__ == "__main__":"""

target = """if __name__ == "__main__":"""

assert normalize(target) in text_norm, "target not found in app.py"

text_norm = text_norm.replace(normalize(target), normalize(route_code), 1)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text_norm)

print("Added /api/calculators/ai-insight route to app.py successfully!")

