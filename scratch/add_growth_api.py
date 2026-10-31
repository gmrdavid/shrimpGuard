with open("app.py", "rb") as f:
    c = f.read().decode("utf-8")

c_norm = c.replace("\r\n", "\n")

new_endpoint = '''
@app.route("/api/growth/calculate", methods=["GET", "POST"])
def calculate_growth_metrics():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True) or {}
    if request.method == "GET":
        data = request.args

    from growth_service import (
        calculate_survival_rate,
        calculate_final_avg_body_weight,
        calculate_daily_gain_and_sgr,
        calculate_biomasses,
        calculate_fcr,
        calculate_fulton_condition,
        calculate_full_growth_suite
    )

    calc_type = str(data.get("type", "all")).strip().lower()

    try:
        if calc_type == "sr":
            return jsonify(calculate_survival_rate(data.get("is", 0), data.get("lhc", 0)))
        elif calc_type == "fabw":
            return jsonify(calculate_final_avg_body_weight(data.get("bw", 0), data.get("lhc", 0), data.get("unit", "kg")))
        elif calc_type == "growth":
            return jsonify(calculate_daily_gain_and_sgr(data.get("ibw", 0), data.get("fabw", 0), data.get("doc", 0)))
        elif calc_type == "biomass":
            return jsonify(calculate_biomasses(data.get("is", 0), data.get("ibw", 0), data.get("lhc", 0), data.get("fabw", 0)))
        elif calc_type == "fcr":
            return jsonify(calculate_fcr(data.get("tfg", 0), data.get("fb", 0), data.get("ib", 0), data.get("feed_unit", "kg"), data.get("biomass_unit", "kg")))
        elif calc_type == "k":
            return jsonify(calculate_fulton_condition(data.get("fabw", 0), data.get("tl", 0)))
        else:
            return jsonify(calculate_full_growth_suite(
                initial_stocking=data.get("is", 100000),
                live_harvest_count=data.get("lhc", 85000),
                days_of_culture=data.get("doc", 90),
                initial_body_weight=data.get("ibw", 0.01),
                bulk_weight=data.get("bw", 1700),
                final_avg_body_weight=data.get("fabw"),
                total_feed_given=data.get("tfg", 2125),
                total_length=data.get("tl", 12.9),
                bulk_weight_unit=data.get("bw_unit", "kg"),
                feed_unit=data.get("feed_unit", "kg")
            ))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":'''

target = 'if __name__ == "__main__":'
if target in c_norm:
    c_norm = c_norm.replace(target, new_endpoint.lstrip())
    with open("app.py", "wb") as f:
        f.write(c_norm.replace("\n", "\r\n").encode("utf-8"))
    print("Added /api/growth/calculate endpoint to app.py successfully!")
else:
    print("Target not found in app.py!")

