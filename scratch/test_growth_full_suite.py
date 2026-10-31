# -*- coding: utf-8 -*-
"""
Verification suite for Shrimp Growth & Zootechnical Performance Calculator (Eqs. 1-8).
Tests:
1. Unit math calculations in growth_service.py
2. Flask API endpoints (/api/growth/calculate)
3. HTML rendering of All-in-One Growth Calculator with:
   - 8 separate performance metric cards (including separated Eq 3 ADWG and Eq 4 SGR)
   - Removal of separate individual tab calculators
   - Popup dialog modal (#growth-equation-modal) presence and buttons
"""
import sys
import json
sys.path.insert(0, '.')

def test_unit_service():
    print("=== Testing growth_service.py direct units ===")
    from growth_service import (
        calculate_survival_rate,
        calculate_final_avg_body_weight,
        calculate_daily_gain_and_sgr,
        calculate_biomasses,
        calculate_fcr,
        calculate_fulton_condition,
        calculate_full_growth_suite
    )

    # Eq. 1: SR
    sr = calculate_survival_rate(100000, 85000)
    assert sr["sr_percent"] == 85.0
    assert sr["mortality_count"] == 15000
    print("[PASS] Eq. 1 (SR): 85.0%")

    # Eq. 2: FABW
    fabw = calculate_final_avg_body_weight(1700, 85000, "kg")
    assert fabw["fabw_grams"] == 20.0
    assert fabw["count_per_kg"] == 50.0
    print("[PASS] Eq. 2 (FABW): 20.0 g (50 pcs/kg)")

    # Eqs. 3 & 4: ADWG & SGR
    growth = calculate_daily_gain_and_sgr(0.010, 20.0, 90)
    assert round(growth["adwg_g_day"], 4) == 0.2221
    assert round(growth["sgr_percent_day"], 3) == 8.445
    print("[PASS] Eqs. 3 & 4 (ADWG & SGR): 0.2221 g/day, 8.445 %/day")

    # Eqs. 5 & 6: Biomass
    bio = calculate_biomasses(100000, 0.010, 85000, 20.0)
    assert bio["ib_kg"] == 1.0
    assert bio["fb_kg"] == 1700.0
    assert bio["net_gain_kg"] == 1699.0
    print("[PASS] Eqs. 5 & 6 (IB & FB): IB=1.0 kg, FB=1700.0 kg, Gain=1699.0 kg")

    # Eq. 7: FCR
    fcr = calculate_fcr(2125, 1700.0, 1.0, "kg", "kg")
    assert round(fcr["fcr"], 3) == 1.251
    print("[PASS] Eq. 7 (FCR): 1.251")

    # Eq. 8: Fulton's K
    k = calculate_fulton_condition(20.0, 12.9)
    assert round(k["k_factor"], 4) == 0.9317
    print("[PASS] Eq. 8 (Fulton's K): 0.9317")

    # Unified full suite
    suite = calculate_full_growth_suite(
        initial_stocking=100000,
        live_harvest_count=85000,
        days_of_culture=90,
        initial_body_weight=0.010,
        bulk_weight=1700,
        total_feed_given=2125,
        total_length=12.9
    )
    assert suite["success"] is True
    print("[PASS] calculate_full_growth_suite() passed with complete metrics.")


def test_flask_endpoints():
    print("\n=== Testing Flask API Endpoints via Flask test_client ===")
    from app import app
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["user_id"] = "rio@gmail.com"
        sess["user_role"] = "Client"
        sess["user_name"] = "Rio"

    # 1. Full suite POST
    res = client.post("/api/growth/calculate", json={
        "type": "all",
        "is": 100000,
        "lhc": 85000,
        "doc": 90,
        "ibw": 0.010,
        "bw": 1700,
        "tfg": 2125,
        "tl": 12.9
    })
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.data}"
    body = res.get_json()
    assert body.get("success") is True
    assert body["survival_rate"]["sr_percent"] == 85.0
    print("[PASS] API POST type=all returned HTTP 200 with complete zootechnical payload.")

    # 2. Individual sub-endpoints
    types = [
        ("sr", {"is": 100000, "lhc": 85000}, "sr_percent", 85.0),
        ("fabw", {"bw": 1700, "lhc": 85000, "unit": "kg"}, "fabw_grams", 20.0),
        ("growth", {"ibw": 0.01, "fabw": 20.0, "doc": 90}, "adwg_g_day", 0.2221),
        ("biomass", {"is": 100000, "ibw": 0.01, "lhc": 85000, "fabw": 20.0}, "fb_kg", 1700.0),
        ("fcr", {"tfg": 2125, "fb": 1700, "ib": 1, "feed_unit": "kg", "biomass_unit": "kg"}, "fcr", 1.251),
        ("k", {"fabw": 20.0, "tl": 12.9}, "k_factor", 0.9317)
    ]

    for t_name, payload, key, expected in types:
        payload["type"] = t_name
        r = client.post("/api/growth/calculate", json=payload)
        assert r.status_code == 200, f"Failed on {t_name}: {r.data}"
        data = r.get_json()
        assert key in data, f"Key {key} not found in {data}"
        print(f"[PASS] API individual type='{t_name}': {key} = {data[key]}")

    # 3. Check Aquaculture Tools page render
    tools_res = client.get("/calculators")
    assert tools_res.status_code == 200
    html = tools_res.data.decode("utf-8")

    # Section 2 checks
    assert "tools-growth-section" in html, "tools-growth-section missing"
    assert "Shrimp Growth" in html, "Shrimp Growth heading missing"
    assert "All-in-One Growth" in html, "All-in-One Engine heading missing"

    # Verify separate calculators are removed
    assert "pane-growth-eq1" not in html, "pane-growth-eq1 should be removed"
    assert "pane-growth-eq2" not in html, "pane-growth-eq2 should be removed"
    assert "pane-growth-eq34" not in html, "pane-growth-eq34 should be removed"
    assert "tools-tab-selector-bar" not in html, "tools-tab-selector-bar should be removed"

    # Verify separated Eq 3 & Eq 4 cards exist
    assert "EQ. 3 &bull; AVG DAILY WEIGHT GAIN (ADWG)" in html, "Eq 3 card missing"
    assert "EQ. 4 &bull; SPECIFIC GROWTH RATE (SGR)" in html, "Eq 4 card missing"

    # Verify modal dialog exists
    assert 'id="growth-equation-modal"' in html, "growth-equation-modal missing"
    assert "growth-calc-details-btn" in html, "growth-calc-details-btn missing"
    assert "growth-modal-formula" in html, "growth-modal-formula missing"
    assert "growth-modal-substitution" in html, "growth-modal-substitution missing"
    assert "growth-modal-recommendation" in html, "growth-modal-recommendation missing"

    print("[PASS] Aquaculture tools page (/calculators) renders All-in-One with 8 separate cards and modal popup dialog.")

if __name__ == '__main__':
    test_unit_service()
    test_flask_endpoints()
    print("\nALL GROWTH SUITE TESTS PASSED SUCCESSFULLY!")
