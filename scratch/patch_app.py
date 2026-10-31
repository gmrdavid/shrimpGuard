import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Check if AquacultureCalculation is already in app.py
if "class AquacultureCalculation(db.Model):" not in content:
    model_code = '''
# --- TABLE 4: AQUACULTURE CALCULATIONS ---
class AquacultureCalculation(db.Model):
    __tablename__ = "aquaculture_calculations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(255), nullable=True, index=True)
    user_name = db.Column(db.String(80), nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    # 1. Estimated Standing Biomass
    pond_area_m2 = db.Column(db.Float, nullable=True)
    pond_depth_m = db.Column(db.Float, nullable=True)
    stocking_density_pl_m2 = db.Column(db.Float, nullable=True)
    survival_rate_pct = db.Column(db.Float, nullable=True)
    abw_g = db.Column(db.Float, nullable=True)
    standing_biomass_kg = db.Column(db.Float, nullable=True)
    standing_biomass_tons = db.Column(db.Float, nullable=True)
    active_shrimp_count = db.Column(db.BigInteger, nullable=True)

    # 2. Temperature Feeding Adjustment
    water_temperature_c = db.Column(db.Float, nullable=True)
    base_feeding_rate_pct = db.Column(db.Float, nullable=True)
    temp_feeding_factor = db.Column(db.Float, nullable=True)
    adjusted_daily_feed_kg = db.Column(db.Float, nullable=True)
    feed_per_meal_kg = db.Column(db.Float, nullable=True)
    feedings_per_day = db.Column(db.Integer, nullable=True)

    # 3. Eight Equations (Eqs. 1–8)
    is_count = db.Column(db.BigInteger, nullable=True)
    lhc_count = db.Column(db.BigInteger, nullable=True)
    doc_days = db.Column(db.Integer, nullable=True)
    ibw_g = db.Column(db.Float, nullable=True)
    bulk_weight_kg = db.Column(db.Float, nullable=True)
    total_feed_given_kg = db.Column(db.Float, nullable=True)
    total_length_cm = db.Column(db.Float, nullable=True)
    eq1_sr_pct = db.Column(db.Float, nullable=True)
    eq1_mortality_count = db.Column(db.BigInteger, nullable=True)
    eq2_fabw_g = db.Column(db.Float, nullable=True)
    eq2_count_per_kg = db.Column(db.Float, nullable=True)
    eq3_adwg_g_day = db.Column(db.Float, nullable=True)
    eq3_weekly_gain_g = db.Column(db.Float, nullable=True)
    eq4_sgr_pct_day = db.Column(db.Float, nullable=True)
    eq5_ib_kg = db.Column(db.Float, nullable=True)
    eq6_fb_kg = db.Column(db.Float, nullable=True)
    eq5_6_net_biomass_kg = db.Column(db.Float, nullable=True)
    eq7_fcr = db.Column(db.Float, nullable=True)
    eq7_feed_efficiency_pct = db.Column(db.Float, nullable=True)
    eq8_fulton_k = db.Column(db.Float, nullable=True)
    eq8_fulton_profile = db.Column(db.String(100), nullable=True)

    # 4. pH Liming Dosage
    lime_pond_vol_m3 = db.Column(db.Float, nullable=True)
    lime_current_ph = db.Column(db.Float, nullable=True)
    lime_target_ph = db.Column(db.Float, nullable=True)
    lime_chemical_type = db.Column(db.String(100), nullable=True)
    lime_dosage_kg = db.Column(db.Float, nullable=True)
    lime_dosage_ppm = db.Column(db.Float, nullable=True)

    # 5. Organic Carbon Dosing (Biofloc C:N)
    molasses_daily_feed_kg = db.Column(db.Float, nullable=True)
    molasses_protein_pct = db.Column(db.Float, nullable=True)
    molasses_target_cn = db.Column(db.Float, nullable=True)
    molasses_carbon_source = db.Column(db.String(100), nullable=True)
    molasses_dosage_kg = db.Column(db.Float, nullable=True)

    # 6. Aerator Power Sizing
    aero_biomass_kg = db.Column(db.Float, nullable=True)
    aero_water_temp_c = db.Column(db.Float, nullable=True)
    aero_salinity_ppt = db.Column(db.Float, nullable=True)
    aero_target_do_ppm = db.Column(db.Float, nullable=True)
    aero_power_hp = db.Column(db.Float, nullable=True)
    aero_units_desc = db.Column(db.String(100), nullable=True)

    # 7. Unionized Ammonia (NH3) Toxicity
    ammonia_tan_ppm = db.Column(db.Float, nullable=True)
    ammonia_temp_c = db.Column(db.Float, nullable=True)
    ammonia_ph = db.Column(db.Float, nullable=True)
    ammonia_salinity_ppt = db.Column(db.Float, nullable=True)
    ammonia_factor_f = db.Column(db.Float, nullable=True)
    ammonia_nh3_ppm = db.Column(db.Float, nullable=True)
    ammonia_status = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_email": self.user_email,
            "user_name": self.user_name,
            "notes": self.notes,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "pond_area_m2": self.pond_area_m2,
            "pond_depth_m": self.pond_depth_m,
            "stocking_density_pl_m2": self.stocking_density_pl_m2,
            "survival_rate_pct": self.survival_rate_pct,
            "abw_g": self.abw_g,
            "standing_biomass_kg": self.standing_biomass_kg,
            "standing_biomass_tons": self.standing_biomass_tons,
            "active_shrimp_count": self.active_shrimp_count,
            "water_temperature_c": self.water_temperature_c,
            "base_feeding_rate_pct": self.base_feeding_rate_pct,
            "temp_feeding_factor": self.temp_feeding_factor,
            "adjusted_daily_feed_kg": self.adjusted_daily_feed_kg,
            "feed_per_meal_kg": self.feed_per_meal_kg,
            "feedings_per_day": self.feedings_per_day,
            "is_count": self.is_count,
            "lhc_count": self.lhc_count,
            "doc_days": self.doc_days,
            "ibw_g": self.ibw_g,
            "bulk_weight_kg": self.bulk_weight_kg,
            "total_feed_given_kg": self.total_feed_given_kg,
            "total_length_cm": self.total_length_cm,
            "eq1_sr_pct": self.eq1_sr_pct,
            "eq1_mortality_count": self.eq1_mortality_count,
            "eq2_fabw_g": self.eq2_fabw_g,
            "eq2_count_per_kg": self.eq2_count_per_kg,
            "eq3_adwg_g_day": self.eq3_adwg_g_day,
            "eq3_weekly_gain_g": self.eq3_weekly_gain_g,
            "eq4_sgr_pct_day": self.eq4_sgr_pct_day,
            "eq5_ib_kg": self.eq5_ib_kg,
            "eq6_fb_kg": self.eq6_fb_kg,
            "eq5_6_net_biomass_kg": self.eq5_6_net_biomass_kg,
            "eq7_fcr": self.eq7_fcr,
            "eq7_feed_efficiency_pct": self.eq7_feed_efficiency_pct,
            "eq8_fulton_k": self.eq8_fulton_k,
            "eq8_fulton_profile": self.eq8_fulton_profile,
            "lime_pond_vol_m3": self.lime_pond_vol_m3,
            "lime_current_ph": self.lime_current_ph,
            "lime_target_ph": self.lime_target_ph,
            "lime_chemical_type": self.lime_chemical_type,
            "lime_dosage_kg": self.lime_dosage_kg,
            "lime_dosage_ppm": self.lime_dosage_ppm,
            "molasses_daily_feed_kg": self.molasses_daily_feed_kg,
            "molasses_protein_pct": self.molasses_protein_pct,
            "molasses_target_cn": self.molasses_target_cn,
            "molasses_carbon_source": self.molasses_carbon_source,
            "molasses_dosage_kg": self.molasses_dosage_kg,
            "aero_biomass_kg": self.aero_biomass_kg,
            "aero_water_temp_c": self.aero_water_temp_c,
            "aero_salinity_ppt": self.aero_salinity_ppt,
            "aero_target_do_ppm": self.aero_target_do_ppm,
            "aero_power_hp": self.aero_power_hp,
            "aero_units_desc": self.aero_units_desc,
            "ammonia_tan_ppm": self.ammonia_tan_ppm,
            "ammonia_temp_c": self.ammonia_temp_c,
            "ammonia_ph": self.ammonia_ph,
            "ammonia_salinity_ppt": self.ammonia_salinity_ppt,
            "ammonia_factor_f": self.ammonia_factor_f,
            "ammonia_nh3_ppm": self.ammonia_nh3_ppm,
            "ammonia_status": self.ammonia_status,
        }
'''
    target = 'def log_activity(action, details=None, user_email=None, user_name=None, role=None, ip_address=None):'
    if target in content:
        content = content.replace(target, model_code + "\n\n" + target)
        print("Inserted AquacultureCalculation model")
    else:
        print("ERROR: Target for model not found")

# 2. Check if endpoints are added
if "/api/calculators/export" not in content:
    routes_code = '''
# =============================================================================
# AQUACULTURE CALCULATORS & DECISION SUPPORT ENDPOINTS
# =============================================================================

AQUACULTURE_EXPORT_CATEGORIES = {
    "biomass": {
        "title": "Estimated Standing Biomass",
        "columns": [
            ("Pond Area (m²)", "pond_area_m2"),
            ("Pond Depth (m)", "pond_depth_m"),
            ("Stocking Density (PL/m²)", "stocking_density_pl_m2"),
            ("Survival Rate (%)", "survival_rate_pct"),
            ("Avg Body Weight - ABW (g)", "abw_g"),
            ("Estimated Active Shrimp Count", "active_shrimp_count"),
            ("Standing Biomass (kg)", "standing_biomass_kg"),
            ("Standing Biomass (Tons)", "standing_biomass_tons"),
        ],
    },
    "temp_feed": {
        "title": "Temperature Feeding Adjustment",
        "columns": [
            ("Water Temperature (°C)", "water_temperature_c"),
            ("Base Feeding Rate (% Biomass)", "base_feeding_rate_pct"),
            ("Temp Adjustment Factor (%)", "temp_feeding_factor"),
            ("Adjusted Daily Feed (kg/day)", "adjusted_daily_feed_kg"),
            ("Feedings Per Day", "feedings_per_day"),
            ("Feed Per Meal (kg/meal)", "feed_per_meal_kg"),
        ],
    },
    "growth": {
        "title": "Eight Growth Performance Equations",
        "columns": [
            ("Initial Stocking Count (IS)", "is_count"),
            ("Live Harvest Count (LHC)", "lhc_count"),
            ("Days of Culture (DOC)", "doc_days"),
            ("Initial Body Weight - IBW (g)", "ibw_g"),
            ("Harvest Bulk Weight - BW (kg)", "bulk_weight_kg"),
            ("Total Feed Given - TFG (kg)", "total_feed_given_kg"),
            ("Total Shrimp Length - TL (cm)", "total_length_cm"),
            ("Eq 1: Survival Rate - SR (%)", "eq1_sr_pct"),
            ("Eq 1: Total Mortality Count", "eq1_mortality_count"),
            ("Eq 2: Final Avg Body Weight - FABW (g)", "eq2_fabw_g"),
            ("Eq 2: Harvest Count per kg", "eq2_count_per_kg"),
            ("Eq 3: Daily Weight Gain - ADWG (g/day)", "eq3_adwg_g_day"),
            ("Eq 3: Weekly Weight Gain (g/week)", "eq3_weekly_gain_g"),
            ("Eq 4: Specific Growth Rate - SGR (%/day)", "eq4_sgr_pct_day"),
            ("Eq 5: Initial Biomass - IB (kg)", "eq5_ib_kg"),
            ("Eq 6: Final Biomass - FB (kg)", "eq6_fb_kg"),
            ("Net Biomass Gain (kg)", "eq5_6_net_biomass_kg"),
            ("Eq 7: Feed Conversion Ratio - FCR", "eq7_fcr"),
            ("Eq 7: Feed Conversion Efficiency (%)", "eq7_feed_efficiency_pct"),
            ("Eq 8: Fulton Condition Factor - K", "eq8_fulton_k"),
            ("Eq 8: Morphological Profile", "eq8_fulton_profile"),
        ],
    },
    "lime": {
        "title": "pH Liming Dosage",
        "columns": [
            ("Liming Pond Volume (m³)", "lime_pond_vol_m3"),
            ("Current Pond pH", "lime_current_ph"),
            ("Target Pond pH", "lime_target_ph"),
            ("Neutralizing Compound", "lime_chemical_type"),
            ("Lime Dosage (kg)", "lime_dosage_kg"),
            ("Lime Application Rate (ppm)", "lime_dosage_ppm"),
        ],
    },
    "carbon": {
        "title": "Organic Carbon Dosing (Biofloc C:N)",
        "columns": [
            ("Biofloc Daily Feed (kg/day)", "molasses_daily_feed_kg"),
            ("Feed Crude Protein (%)", "molasses_protein_pct"),
            ("Target C:N Ratio", "molasses_target_cn"),
            ("Carbon Source Type", "molasses_carbon_source"),
            ("Carbon Required (kg/day)", "molasses_dosage_kg"),
        ],
    },
    "aeration": {
        "title": "Aerator Power Sizing",
        "columns": [
            ("Aeration Pond Biomass (kg)", "aero_biomass_kg"),
            ("Water Temp for Aeration (°C)", "aero_water_temp_c"),
            ("Salinity for Aeration (ppt)", "aero_salinity_ppt"),
            ("Target DO (mg/L)", "aero_target_do_ppm"),
            ("Required Aerator Power (HP)", "aero_power_hp"),
            ("Suggested Aerator Units", "aero_units_desc"),
        ],
    },
    "ammonia": {
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
}


def generate_custom_excel(sheet_name, headers, rows):
    def get_column_letter(col_idx):
        result = ""
        while col_idx > 0:
            col_idx, remainder = divmod(col_idx - 1, 26)
            result = chr(65 + remainder) + result
        return result

    worksheet_rows = []
    # Header row (row 1)
    header_cells = [
        f'<c r="{get_column_letter(idx)}1" t="inlineStr"><is><t xml:space="preserve">{escape(str(h))}</t></is></c>'
        for idx, h in enumerate(headers, start=1)
    ]
    worksheet_rows.append(f'<row r="1">{"".join(header_cells)}</row>')

    # Data rows
    for r_idx, row in enumerate(rows, start=2):
        row_cells = []
        for c_idx, val in enumerate(row, start=1):
            cell_ref = f"{get_column_letter(c_idx)}{r_idx}"
            if val is None or val == "":
                continue
            if isinstance(val, (int, float)) and math.isfinite(val):
                row_cells.append(f'<c r="{cell_ref}"><v>{val}</v></c>')
            else:
                row_cells.append(
                    f'<c r="{cell_ref}" t="inlineStr"><is><t xml:space="preserve">{escape(str(val))}</t></is></c>'
                )
        worksheet_rows.append(f'<row r="{r_idx}">{"".join(row_cells)}</row>')

    worksheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(worksheet_rows)}</sheetData></worksheet>'
    )
    workbook = io.BytesIO()
    with zipfile.ZipFile(workbook, "w", zipfile.ZIP_DEFLATED) as excel_file:
        excel_file.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>",
        )
        excel_file.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>",
        )
        clean_sheet_name = re.sub(r'[\/\\\\?\\*\\[\\]:]', '', sheet_name)[:31] or "Calculations"
        excel_file.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f'<sheets><sheet name="{escape(clean_sheet_name)}" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        excel_file.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            "</Relationships>",
        )
        excel_file.writestr("xl/worksheets/sheet1.xml", worksheet)

    workbook.seek(0)
    return workbook


@app.route("/api/calculators/save", methods=["POST"])
@role_required("Client")
def save_aquaculture_calculation():
    user_email = session.get("user_id")
    user = db.session.get(User, user_email) if user_email else None
    data = request.get_json(silent=True) or {}

    def safe_flt(v):
        if v is None or v == "":
            return None
        try:
            val = float(v)
            return val if math.isfinite(val) else None
        except (ValueError, TypeError):
            return None

    def safe_integer(v):
        if v is None or v == "":
            return None
        try:
            return int(round(float(v)))
        except (ValueError, TypeError):
            return None

    try:
        notes_str = str(data.get("notes") or "").strip()[:255]
        if not notes_str:
            notes_str = f"Pond Calculation - {datetime.now().strftime('%b %d, %Y %H:%M')}"

        record = AquacultureCalculation(
            user_email=user_email,
            user_name=user.name if user else "Client",
            notes=notes_str,
            # 1. Biomass & Feed
            pond_area_m2=safe_flt(data.get("pond_area_m2")),
            pond_depth_m=safe_flt(data.get("pond_depth_m")),
            stocking_density_pl_m2=safe_flt(data.get("stocking_density_pl_m2")),
            survival_rate_pct=safe_flt(data.get("survival_rate_pct")),
            abw_g=safe_flt(data.get("abw_g")),
            standing_biomass_kg=safe_flt(data.get("standing_biomass_kg")),
            standing_biomass_tons=safe_flt(data.get("standing_biomass_tons")),
            active_shrimp_count=safe_integer(data.get("active_shrimp_count")),
            # 2. Temperature Feeding
            water_temperature_c=safe_flt(data.get("water_temperature_c")),
            base_feeding_rate_pct=safe_flt(data.get("base_feeding_rate_pct")),
            temp_feeding_factor=safe_flt(data.get("temp_feeding_factor")),
            adjusted_daily_feed_kg=safe_flt(data.get("adjusted_daily_feed_kg")),
            feed_per_meal_kg=safe_flt(data.get("feed_per_meal_kg")),
            feedings_per_day=safe_integer(data.get("feedings_per_day")),
            # 3. Eight Growth Equations (Eqs. 1–8)
            is_count=safe_integer(data.get("is_count")),
            lhc_count=safe_integer(data.get("lhc_count")),
            doc_days=safe_integer(data.get("doc_days")),
            ibw_g=safe_flt(data.get("ibw_g")),
            bulk_weight_kg=safe_flt(data.get("bulk_weight_kg")),
            total_feed_given_kg=safe_flt(data.get("total_feed_given_kg")),
            total_length_cm=safe_flt(data.get("total_length_cm")),
            eq1_sr_pct=safe_flt(data.get("eq1_sr_pct")),
            eq1_mortality_count=safe_integer(data.get("eq1_mortality_count")),
            eq2_fabw_g=safe_flt(data.get("eq2_fabw_g")),
            eq2_count_per_kg=safe_flt(data.get("eq2_count_per_kg")),
            eq3_adwg_g_day=safe_flt(data.get("eq3_adwg_g_day")),
            eq3_weekly_gain_g=safe_flt(data.get("eq3_weekly_gain_g")),
            eq4_sgr_pct_day=safe_flt(data.get("eq4_sgr_pct_day")),
            eq5_ib_kg=safe_flt(data.get("eq5_ib_kg")),
            eq6_fb_kg=safe_flt(data.get("eq6_fb_kg")),
            eq5_6_net_biomass_kg=safe_flt(data.get("eq5_6_net_biomass_kg")),
            eq7_fcr=safe_flt(data.get("eq7_fcr")),
            eq7_feed_efficiency_pct=safe_flt(data.get("eq7_feed_efficiency_pct")),
            eq8_fulton_k=safe_flt(data.get("eq8_fulton_k")),
            eq8_fulton_profile=str(data.get("eq8_fulton_profile") or "").strip()[:100] or None,
            # 4. pH Liming
            lime_pond_vol_m3=safe_flt(data.get("lime_pond_vol_m3")),
            lime_current_ph=safe_flt(data.get("lime_current_ph")),
            lime_target_ph=safe_flt(data.get("lime_target_ph")),
            lime_chemical_type=str(data.get("lime_chemical_type") or "").strip()[:100] or None,
            lime_dosage_kg=safe_flt(data.get("lime_dosage_kg")),
            lime_dosage_ppm=safe_flt(data.get("lime_dosage_ppm")),
            # 5. Organic Carbon Dosing
            molasses_daily_feed_kg=safe_flt(data.get("molasses_daily_feed_kg")),
            molasses_protein_pct=safe_flt(data.get("molasses_protein_pct")),
            molasses_target_cn=safe_flt(data.get("molasses_target_cn")),
            molasses_carbon_source=str(data.get("molasses_carbon_source") or "").strip()[:100] or None,
            molasses_dosage_kg=safe_flt(data.get("molasses_dosage_kg")),
            # 6. Aerator Power
            aero_biomass_kg=safe_flt(data.get("aero_biomass_kg")),
            aero_water_temp_c=safe_flt(data.get("aero_water_temp_c")),
            aero_salinity_ppt=safe_flt(data.get("aero_salinity_ppt")),
            aero_target_do_ppm=safe_flt(data.get("aero_target_do_ppm")),
            aero_power_hp=safe_flt(data.get("aero_power_hp")),
            aero_units_desc=str(data.get("aero_units_desc") or "").strip()[:100] or None,
            # 7. Unionized Ammonia
            ammonia_tan_ppm=safe_flt(data.get("ammonia_tan_ppm")),
            ammonia_temp_c=safe_flt(data.get("ammonia_temp_c")),
            ammonia_ph=safe_flt(data.get("ammonia_ph")),
            ammonia_salinity_ppt=safe_flt(data.get("ammonia_salinity_ppt")),
            ammonia_factor_f=safe_flt(data.get("ammonia_factor_f")),
            ammonia_nh3_ppm=safe_flt(data.get("ammonia_nh3_ppm")),
            ammonia_status=str(data.get("ammonia_status") or "").strip()[:50] or None,
        )

        db.session.add(record)
        db.session.commit()

        log_activity(
            "Aquaculture Calculation Saved",
            f"Record #{record.id} saved for {user.name if user else 'Client'} ({record.notes})",
            user_email=user_email,
            user_name=user.name if user else "Client",
            role="Client",
        )

        return jsonify({
            "success": True,
            "id": record.id,
            "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "notes": record.notes,
            "message": f"Calculation snapshot #{record.id} successfully saved to database.",
        })
    except Exception as exc:
        db.session.rollback()
        app.logger.exception("Failed to save aquaculture calculation record.")
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/calculators/history", methods=["GET"])
@role_required("Client")
def get_aquaculture_history():
    try:
        count = db.session.query(func.count(AquacultureCalculation.id)).scalar() or 0
        latest_records = (
            AquacultureCalculation.query.order_by(AquacultureCalculation.created_at.desc())
            .limit(10)
            .all()
        )
        return jsonify({
            "success": True,
            "total_count": count,
            "latest": [r.to_dict() for r in latest_records],
        })
    except Exception as exc:
        app.logger.exception("Failed to query calculation history.")
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/calculators/export", methods=["GET", "POST"])
@role_required("Client")
def export_aquaculture_calculations():
    payload = request.get_json(silent=True) or {}
    
    categories_raw = (
        payload.get("categories")
        or request.args.get("categories")
        or request.form.get("categories")
        or "all"
    )
    scope = (
        str(payload.get("scope") or request.args.get("scope") or request.form.get("scope") or "saved")
        .strip()
        .lower()
    )
    date_filter = (
        str(payload.get("date") or request.args.get("date") or request.form.get("date") or "all")
        .strip()
        .lower()
    )
    export_format = (
        str(payload.get("format") or request.args.get("format") or request.form.get("format") or "xlsx")
        .strip()
        .lower()
    )
    if export_format not in ("xlsx", "csv"):
        export_format = "xlsx"

    # Parse categories to export
    if isinstance(categories_raw, list):
        selected_cats = [c.strip().lower() for c in categories_raw if c.strip().lower() in AQUACULTURE_EXPORT_CATEGORIES]
    elif isinstance(categories_raw, str):
        if categories_raw.lower() in ("all", "*", ""):
            selected_cats = list(AQUACULTURE_EXPORT_CATEGORIES.keys())
        else:
            selected_cats = [c.strip().lower() for c in categories_raw.split(",") if c.strip().lower() in AQUACULTURE_EXPORT_CATEGORIES]
    else:
        selected_cats = list(AQUACULTURE_EXPORT_CATEGORIES.keys())

    if not selected_cats:
        selected_cats = list(AQUACULTURE_EXPORT_CATEGORIES.keys())

    # Build Header Row
    headers = ["Record ID", "Recorded Date & Time", "Notes / Pond ID", "Operator"]
    columns_spec = []  # list of tuples: (header_name, col_attr)
    for cat in selected_cats:
        cat_info = AQUACULTURE_EXPORT_CATEGORIES[cat]
        for col_title, col_attr in cat_info["columns"]:
            headers.append(col_title)
            columns_spec.append(col_attr)

    rows = []

    if scope == "current":
        # Exporting current screen values passed in payload or fallback default
        current_data = payload.get("current_data") or {}
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_email = session.get("user_id")
        user = db.session.get(User, user_email) if user_email else None
        operator_name = user.name if user else "Client"
        notes_val = str(current_data.get("notes") or "Active Screen Calculation Snapshot").strip()

        row = ["Snapshot", now_str, notes_val, operator_name]
        for col_attr in columns_spec:
            val = current_data.get(col_attr)
            if val is not None and isinstance(val, (int, float)):
                row.append(val)
            elif val is not None and str(val).strip() != "":
                try:
                    num = float(val)
                    row.append(num if math.isfinite(num) else str(val))
                except (ValueError, TypeError):
                    row.append(str(val))
            else:
                row.append("")
        rows.append(row)
    else:
        # Exporting from database records
        query = AquacultureCalculation.query.order_by(AquacultureCalculation.created_at.desc())

        # Date filtering
        now = datetime.now()
        if date_filter == "today":
            start_today = datetime(now.year, now.month, now.day)
            query = query.filter(AquacultureCalculation.created_at >= start_today)
        elif date_filter == "7d":
            start_7d = now - timedelta(days=7)
            query = query.filter(AquacultureCalculation.created_at >= start_7d)
        elif date_filter == "30d":
            start_30d = now - timedelta(days=30)
            query = query.filter(AquacultureCalculation.created_at >= start_30d)
        elif date_filter != "all" and re.match(r"^\\d{4}-\\d{2}-\\d{2}$", date_filter):
            try:
                dt_obj = datetime.strptime(date_filter, "%Y-%m-%d")
                start_dt = datetime(dt_obj.year, dt_obj.month, dt_obj.day)
                end_dt = start_dt + timedelta(days=1)
                query = query.filter(AquacultureCalculation.created_at >= start_dt, AquacultureCalculation.created_at < end_dt)
            except ValueError:
                pass

        records = query.all()

        if not records:
            # Placeholder if database table has no rows matching filter
            rows.append(["No records", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "No calculation records saved for selected filter", session.get("user_id") or "Client"] + ["" for _ in columns_spec])
        else:
            for rec in records:
                rec_dt = rec.created_at.strftime("%Y-%m-%d %H:%M:%S") if rec.created_at else ""
                row = [rec.id, rec_dt, rec.notes or "Pond Run", rec.user_name or "Client"]
                for col_attr in columns_spec:
                    val = getattr(rec, col_attr, None)
                    row.append(val if val is not None else "")
                rows.append(row)

    # Dynamic filename
    timestamp_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
    cat_summary = "all-tools" if len(selected_cats) == len(AQUACULTURE_EXPORT_CATEGORIES) else f"{len(selected_cats)}-modules"
    download_filename = f"shrimpguard-aquaculture-calculations_{cat_summary}_{timestamp_slug}.{export_format}"

    # Log export activity
    log_activity(
        "Aquaculture Calculations Exported",
        f"Exported {len(rows)} records in {export_format.upper()} ({', '.join(selected_cats)})",
    )

    # Return CSV
    if export_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for r in rows:
            writer.writerow(r)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8-sig")),
            as_attachment=True,
            download_name=download_filename,
            mimetype="text/csv",
        )

    # Return Excel (.xlsx)
    excel_stream = generate_custom_excel("Pond Calculations", headers, rows)
    return send_file(
        excel_stream,
        as_attachment=True,
        download_name=download_filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
'''
    target2 = 'return render_template("calculators.html", user=user)'
    if target2 in content:
        idx = content.find(target2) + len(target2)
        content = content[:idx] + "\n\n" + routes_code + content[idx:]
        print("Inserted routes into app.py")
    else:
        print("ERROR: Target for routes not found")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Saved app.py successfully")

