import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Model columns
old_col = """    # 7. Unionized Ammonia (NH3) Toxicity
    ammonia_tan_ppm = db.Column(db.Float, nullable=True)
    ammonia_temp_c = db.Column(db.Float, nullable=True)
    ammonia_ph = db.Column(db.Float, nullable=True)
    ammonia_salinity_ppt = db.Column(db.Float, nullable=True)
    ammonia_factor_f = db.Column(db.Float, nullable=True)
    ammonia_nh3_ppm = db.Column(db.Float, nullable=True)
    ammonia_status = db.Column(db.String(50), nullable=True)"""

new_col = """    # 7. Unionized Ammonia (NH3) Toxicity
    ammonia_tan_ppm = db.Column(db.Float, nullable=True)
    ammonia_temp_c = db.Column(db.Float, nullable=True)
    ammonia_ph = db.Column(db.Float, nullable=True)
    ammonia_salinity_ppt = db.Column(db.Float, nullable=True)
    ammonia_factor_f = db.Column(db.Float, nullable=True)
    ammonia_nh3_ppm = db.Column(db.Float, nullable=True)
    ammonia_status = db.Column(db.String(50), nullable=True)

    # 8. Free Carbon Dioxide (CO2) Concentration
    co2_alkalinity_mg_l = db.Column(db.Float, nullable=True)
    co2_temp_c = db.Column(db.Float, nullable=True)
    co2_ph = db.Column(db.Float, nullable=True)
    co2_factor = db.Column(db.Float, nullable=True)
    co2_concentration_mg_l = db.Column(db.Float, nullable=True)
    co2_status = db.Column(db.String(50), nullable=True)"""

# 2. to_dict
old_dict = """            "ammonia_factor_f": self.ammonia_factor_f,
            "ammonia_nh3_ppm": self.ammonia_nh3_ppm,
            "ammonia_status": self.ammonia_status,
        }"""

new_dict = """            "ammonia_factor_f": self.ammonia_factor_f,
            "ammonia_nh3_ppm": self.ammonia_nh3_ppm,
            "ammonia_status": self.ammonia_status,
            "co2_alkalinity_mg_l": self.co2_alkalinity_mg_l,
            "co2_temp_c": self.co2_temp_c,
            "co2_ph": self.co2_ph,
            "co2_factor": self.co2_factor,
            "co2_concentration_mg_l": self.co2_concentration_mg_l,
            "co2_status": self.co2_status,
        }"""

# 3. Export categories
old_export = """    "ammonia": {
        "title": "Unionized Ammonia (NH3) Toxicity",
        "columns": [
            ("Total Ammonia Nitrogen - TAN (mg/L)", "ammonia_tan_ppm"),
            ("Water Temp for NH3 (°C)", "ammonia_temp_c"),
            ("Water pH for NH3", "ammonia_ph"),
            ("Salinity for NH3 (ppt)", "ammonia_salinity_ppt"),
            ("Un-ionized Fraction - f (%)", "ammonia_factor_f"),
            ("Toxic Un-ionized Ammonia - NH3 (mg/L)", "ammonia_nh3_ppm"),
            ("Ammonia Toxicity Status", "ammonia_status"),
        ],
    },
}"""

new_export = """    "ammonia": {
        "title": "Unionized Ammonia (NH3) Toxicity",
        "columns": [
            ("Total Ammonia Nitrogen - TAN (mg/L)", "ammonia_tan_ppm"),
            ("Water Temp for NH3 (°C)", "ammonia_temp_c"),
            ("Water pH for NH3", "ammonia_ph"),
            ("Salinity for NH3 (ppt)", "ammonia_salinity_ppt"),
            ("Un-ionized Fraction - f (%)", "ammonia_factor_f"),
            ("Toxic Un-ionized Ammonia - NH3 (mg/L)", "ammonia_nh3_ppm"),
            ("Ammonia Toxicity Status", "ammonia_status"),
        ],
    },
    "co2": {
        "title": "Free Carbon Dioxide (CO2) Concentration",
        "columns": [
            ("Total Alkalinity - CaCO3 (mg/L)", "co2_alkalinity_mg_l"),
            ("Water Temp for CO2 (°C)", "co2_temp_c"),
            ("Water pH for CO2", "co2_ph"),
            ("Tucker Factor f", "co2_factor"),
            ("Free CO2 Concentration (mg/L)", "co2_concentration_mg_l"),
            ("CO2 Toxicity Status", "co2_status"),
        ],
    },
}"""

# 4. Save record parsing
old_save = """            # 7. Unionized Ammonia
            ammonia_tan_ppm=safe_flt(data.get("ammonia_tan_ppm")),
            ammonia_temp_c=safe_flt(data.get("ammonia_temp_c")),
            ammonia_ph=safe_flt(data.get("ammonia_ph")),
            ammonia_salinity_ppt=safe_flt(data.get("ammonia_salinity_ppt")),
            ammonia_factor_f=safe_flt(data.get("ammonia_factor_f")),
            ammonia_nh3_ppm=safe_flt(data.get("ammonia_nh3_ppm")),
            ammonia_status=str(data.get("ammonia_status") or "").strip()[:50] or None,
        )"""

new_save = """            # 7. Unionized Ammonia
            ammonia_tan_ppm=safe_flt(data.get("ammonia_tan_ppm")),
            ammonia_temp_c=safe_flt(data.get("ammonia_temp_c")),
            ammonia_ph=safe_flt(data.get("ammonia_ph")),
            ammonia_salinity_ppt=safe_flt(data.get("ammonia_salinity_ppt")),
            ammonia_factor_f=safe_flt(data.get("ammonia_factor_f")),
            ammonia_nh3_ppm=safe_flt(data.get("ammonia_nh3_ppm")),
            ammonia_status=str(data.get("ammonia_status") or "").strip()[:50] or None,
            # 8. Free Carbon Dioxide
            co2_alkalinity_mg_l=safe_flt(data.get("co2_alkalinity_mg_l")),
            co2_temp_c=safe_flt(data.get("co2_temp_c")),
            co2_ph=safe_flt(data.get("co2_ph")),
            co2_factor=safe_flt(data.get("co2_factor")),
            co2_concentration_mg_l=safe_flt(data.get("co2_concentration_mg_l")),
            co2_status=str(data.get("co2_status") or "").strip()[:50] or None,
        )"""

# 5. CO2 API endpoint
old_api = """@app.route("/api/ammonia/calculate", methods=["GET", "POST"])"""

co2_endpoint_code = """@app.route("/api/co2/calculate", methods=["GET", "POST"])
def calculate_co2():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required."}), 401

    data = request.get_json(silent=True) or {}
    if request.method == "GET":
        data = request.args

    alk_raw = data.get("alkalinity")
    if alk_raw is None or str(alk_raw).strip() == "":
        return jsonify({"error": "Total Alkalinity value is required."}), 400

    try:
        alk = float(alk_raw)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid alkalinity value."}), 400

    temp = data.get("temp")
    ph = data.get("ph")

    if temp is None or ph is None or str(temp).strip() == "" or str(ph).strip() == "":
        latest = get_latest_sensor_dict()
        if not latest or latest.get("temperature") is None or latest.get("ph") is None:
            return jsonify({"error": "No sensor readings available to calculate free CO2. Please provide temperature and pH."}), 400
        temp = latest["temperature"]
        ph = latest["ph"]

    try:
        temp = float(temp)
        ph = float(ph)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid temperature or pH value."}), 400

    from co2_service import calculate_free_co2
    result = calculate_free_co2(alk, temp, ph)
    return jsonify(result)


@app.route("/api/ammonia/calculate", methods=["GET", "POST"])"""

def normalize(text):
    return text.replace("\r\n", "\n")

content_norm = normalize(content)
assert normalize(old_col) in content_norm, "old_col not found"
assert normalize(old_dict) in content_norm, "old_dict not found"
assert normalize(old_export) in content_norm, "old_export not found"
assert normalize(old_save) in content_norm, "old_save not found"
assert normalize(old_api) in content_norm, "old_api not found"

content_norm = content_norm.replace(normalize(old_col), normalize(new_col))
content_norm = content_norm.replace(normalize(old_dict), normalize(new_dict))
content_norm = content_norm.replace(normalize(old_export), normalize(new_export))
content_norm = content_norm.replace(normalize(old_save), normalize(new_save))
content_norm = content_norm.replace(normalize(old_api), normalize(co2_endpoint_code))

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content_norm)

print("Successfully updated app.py!")

