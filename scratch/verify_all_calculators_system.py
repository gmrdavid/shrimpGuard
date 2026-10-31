import sys
import os
sys.path.insert(0, os.path.abspath("."))

from app import app, db, User, AquacultureCalculation

print("=" * 60)
print("COMPREHENSIVE AQUACULTURE CALCULATORS & EXPORT VERIFICATION")
print("=" * 60)

with app.app_context():
    # 1. Inspect table
    cols = [c.name for c in AquacultureCalculation.__table__.columns]
    print(f"[1] AquacultureCalculation table has {len(cols)} columns.")
    assert len(cols) == 64, f"Expected 64 columns, got {len(cols)}"

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess["user_id"] = "rio@gmail.com"
        sess["user_role"] = "Client"

    # 2. Test Page Render
    page_resp = client.get("/calculators")
    assert page_resp.status_code == 200, f"Expected 200 for /calculators, got {page_resp.status_code}"
    page_html = page_resp.data.decode("utf-8")
    assert "btn-open-save-modal" in page_html, "Missing btn-open-save-modal in template"
    assert "btn-open-export-modal" in page_html, "Missing btn-open-export-modal in template"
    assert "tools-save-modal" in page_html, "Missing tools-save-modal in template"
    assert "tools-export-modal" in page_html, "Missing tools-export-modal in template"
    print("[2] Page /calculators rendered with Save and Export buttons + modals (HTTP 200)")

    # 3. Test Save Endpoint
    test_run = {
        "notes": "Pond 1 - Sampling Week 8",
        "pond_area_m2": 2500,
        "pond_depth_m": 1.25,
        "stocking_density_pl_m2": 70,
        "survival_rate_pct": 88.0,
        "abw_g": 18.5,
        "standing_biomass_kg": 2849.0,
        "standing_biomass_tons": 2.85,
        "active_shrimp_count": 154000,
        "water_temperature_c": 30.2,
        "base_feeding_rate_pct": 3.1,
        "temp_feeding_factor": 1.0,
        "adjusted_daily_feed_kg": 88.3,
        "feed_per_meal_kg": 22.1,
        "feedings_per_day": 4,
        "is_count": 175000,
        "lhc_count": 154000,
        "doc_days": 90,
        "ibw_g": 0.010,
        "bulk_weight_kg": 2849.0,
        "total_feed_given_kg": 3560.0,
        "total_length_cm": 13.5,
        "eq1_sr_pct": 88.0,
        "eq1_mortality_count": 21000,
        "eq2_fabw_g": 18.5,
        "eq2_count_per_kg": 54.1,
        "eq3_adwg_g_day": 0.205,
        "eq3_weekly_gain_g": 1.438,
        "eq4_sgr_pct_day": 8.35,
        "eq5_ib_kg": 1.75,
        "eq6_fb_kg": 2849.0,
        "eq5_6_net_biomass_kg": 2847.25,
        "eq7_fcr": 1.25,
        "eq7_feed_efficiency_pct": 80.0,
        "eq8_fulton_k": 0.752,
        "eq8_fulton_profile": "Slender / Lean (<0.80)",
        "lime_pond_vol_m3": 3125,
        "lime_current_ph": 7.35,
        "lime_target_ph": 8.00,
        "lime_chemical_type": "Agricultural Limestone (CaCO3)",
        "lime_dosage_kg": 101.6,
        "lime_dosage_ppm": 32.5,
        "molasses_daily_feed_kg": 88.3,
        "molasses_protein_pct": 35,
        "molasses_target_cn": 15,
        "molasses_carbon_source": "Cane Molasses",
        "molasses_dosage_kg": 131.6,
        "aero_biomass_kg": 2849.0,
        "aero_water_temp_c": 30.2,
        "aero_salinity_ppt": 18.0,
        "aero_target_do_ppm": 5.0,
        "aero_power_hp": 9.0,
        "aero_units_desc": "4 × 2-HP + 1 × 1-HP",
        "ammonia_tan_ppm": 0.75,
        "ammonia_temp_c": 30.2,
        "ammonia_ph": 7.85,
        "ammonia_salinity_ppt": 18.0,
        "ammonia_factor_f": 0.052,
        "ammonia_nh3_ppm": 0.039,
        "ammonia_status": "Optimal"
    }

    save_resp = client.post("/api/calculators/save", json=test_run)
    assert save_resp.status_code == 200, f"Expected 200 for save, got {save_resp.status_code}"
    save_data = save_resp.get_json()
    assert save_data.get("success") is True
    rec_id = save_data.get("id")
    print(f"[3] Successfully saved calculation snapshot #{rec_id} to MySQL (HTTP 200)")

    # 4. Test History Endpoint
    hist_resp = client.get("/api/calculators/history")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.get_json()
    assert hist_data["total_count"] >= 1
    print(f"[4] History endpoint confirmed: {hist_data['total_count']} saved records found (HTTP 200)")

    # 5. Test Export XLSX All Modules
    exp_all_resp = client.get("/api/calculators/export?categories=all&format=xlsx")
    assert exp_all_resp.status_code == 200
    assert "spreadsheetml.sheet" in exp_all_resp.content_type
    print(f"[5] Exported all 7 modules to Excel ({len(exp_all_resp.data)} bytes, HTTP 200)")

    # 6. Test Export CSV with custom category selection: growth + ammonia + lime
    exp_custom_resp = client.get("/api/calculators/export?categories=growth,ammonia,lime&format=csv")
    assert exp_custom_resp.status_code == 200
    csv_text = exp_custom_resp.data.decode("utf-8-sig")
    assert "Eq 1: Survival Rate - SR (%)" in csv_text
    assert "Toxic Un-ionized Ammonia - NH3 (mg/L)" in csv_text
    assert "Lime Dosage (kg)" in csv_text
    # Should NOT have carbon dosing or aeration headers because they were excluded!
    assert "Biofloc Daily Feed (kg/day)" not in csv_text
    assert "Required Aerator Power (HP)" not in csv_text
    print(f"[6] Exported customized subset (growth, ammonia, lime) to CSV correctly excluding other categories (HTTP 200)")

    # 7. Test Export Current Snapshot via POST
    exp_cur_resp = client.post("/api/calculators/export", json={
        "scope": "current",
        "categories": ["biomass", "temp_feed"],
        "format": "xlsx",
        "current_data": {
            "notes": "DOC 90 Live Screen Probe",
            "pond_area_m2": 3000,
            "standing_biomass_kg": 3500.0,
            "adjusted_daily_feed_kg": 110.0
        }
    })
    assert exp_cur_resp.status_code == 200
    assert len(exp_cur_resp.data) > 1000
    print(f"[7] Exported active screen snapshot to Excel ({len(exp_cur_resp.data)} bytes, HTTP 200)")

    # 8. Test Client Routes Regression Check
    client_routes = [
        "/",
        "/login",
        "/signup",
        "/dashboard",
        "/monitoring",
        "/historical",
        "/analytics",
        "/alerts",
        "/calculators",
        "/aquaculture-tools",
        "/settings",
        "/api/readings/latest",
        "/api/calculators/history",
    ]
    for r in client_routes:
        res = client.get(r)
        assert res.status_code in (200, 302), f"Route {r} failed with status {res.status_code}"
    print(f"[8] All {len(client_routes)} application routes verified passing (HTTP 200/302).")

print("=" * 60)
print("ALL AQUACULTURE SYSTEM VERIFICATION CHECKS PASSED PERFECTLY!")
print("=" * 60)