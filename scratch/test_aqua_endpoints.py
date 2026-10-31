import sys
import os
sys.path.insert(0, os.path.abspath("."))

import json
from app import app, db, AquacultureCalculation

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess["user_id"] = "rio@gmail.com"
        sess["user_role"] = "Client"

    # Test Save Endpoint
    payload = {
        "notes": "Test Automated Run - Pond Alpha DOC 45",
        "pond_area_m2": 1500,
        "pond_depth_m": 1.2,
        "stocking_density_pl_m2": 60,
        "survival_rate_pct": 86.5,
        "abw_g": 16.8,
        "standing_biomass_kg": 1308.6,
        "standing_biomass_tons": 1.31,
        "active_shrimp_count": 77850,
        "water_temperature_c": 29.4,
        "base_feeding_rate_pct": 3.2,
        "temp_feeding_factor": 1.0,
        "adjusted_daily_feed_kg": 41.9,
        "feed_per_meal_kg": 10.5,
        "feedings_per_day": 4,
        "is_count": 100000,
        "lhc_count": 86500,
        "doc_days": 85,
        "ibw_g": 0.010,
        "bulk_weight_kg": 1453.2,
        "total_feed_given_kg": 1889.0,
        "total_length_cm": 12.8,
        "eq1_sr_pct": 86.5,
        "eq1_mortality_count": 13500,
        "eq2_fabw_g": 16.8,
        "eq2_count_per_kg": 59.5,
        "eq3_adwg_g_day": 0.198,
        "eq3_weekly_gain_g": 1.383,
        "eq4_sgr_pct_day": 8.74,
        "eq5_ib_kg": 1.0,
        "eq6_fb_kg": 1453.2,
        "eq5_6_net_biomass_kg": 1452.2,
        "eq7_fcr": 1.30,
        "eq7_feed_efficiency_pct": 76.9,
        "eq8_fulton_k": 0.801,
        "eq8_fulton_profile": "Optimal Condition (0.80–1.15)",
        "lime_pond_vol_m3": 1800,
        "lime_current_ph": 7.30,
        "lime_target_ph": 8.00,
        "lime_chemical_type": "Agricultural Limestone (CaCO3)",
        "lime_dosage_kg": 63.0,
        "lime_dosage_ppm": 35.0,
        "molasses_daily_feed_kg": 41.9,
        "molasses_protein_pct": 35,
        "molasses_target_cn": 15,
        "molasses_carbon_source": "Cane Molasses",
        "molasses_dosage_kg": 62.5,
        "aero_biomass_kg": 1308.6,
        "aero_water_temp_c": 29.4,
        "aero_salinity_ppt": 18.0,
        "aero_target_do_ppm": 5.0,
        "aero_power_hp": 3.5,
        "aero_units_desc": "1 × 2-HP + 1 × 1-HP",
        "ammonia_tan_ppm": 0.60,
        "ammonia_temp_c": 29.4,
        "ammonia_ph": 7.95,
        "ammonia_salinity_ppt": 18.0,
        "ammonia_factor_f": 0.053,
        "ammonia_nh3_ppm": 0.032,
        "ammonia_status": "Optimal",
    }

    resp = client.post("/api/calculators/save", json=payload)
    print("Save Response:", resp.status_code, resp.get_json())

    # Test History Endpoint
    resp_hist = client.get("/api/calculators/history")
    print("History Response:", resp_hist.status_code, "Count:", resp_hist.get_json().get("total_count"))

    # Test Export Endpoint (All categories, Excel)
    resp_xlsx = client.get("/api/calculators/export?categories=all&format=xlsx")
    print("Export XLSX (All):", resp_xlsx.status_code, len(resp_xlsx.data), "bytes, Content-Type:", resp_xlsx.content_type)

    # Test Export Endpoint (Subset: growth and ammonia, CSV)
    resp_csv = client.get("/api/calculators/export?categories=growth,ammonia&format=csv")
    print("Export CSV (Subset):", resp_csv.status_code, len(resp_csv.data), "bytes, Content-Type:", resp_csv.content_type)
    print("CSV sample:\n", resp_csv.data.decode("utf-8-sig")[:300])

    # Test Export Endpoint (Current scope)
    resp_cur = client.post("/api/calculators/export", json={
        "scope": "current",
        "categories": ["biomass", "temp_feed", "lime"],
        "format": "xlsx",
        "current_data": {
            "notes": "Current Screen Live Snapshot",
            "pond_area_m2": 2000,
            "standing_biomass_kg": 1800,
            "adjusted_daily_feed_kg": 55.0,
            "lime_dosage_kg": 40.0
        }
    })
    print("Export Current Screen XLSX:", resp_cur.status_code, len(resp_cur.data), "bytes")
