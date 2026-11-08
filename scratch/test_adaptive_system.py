import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, ADAPTIVE_PERSONAS, compute_adaptive_persona, get_adaptive_next_action

def test_adaptive_system():
    print("=== Testing ShrimpGuard Adaptive Web System (AWS) ===")
    
    # 1. Test Persona Computation
    # Scenario A: Heavy monitoring
    p_id, p_pcts = compute_adaptive_persona({"monitoring": 20, "calculators": 2}, {"monitoring": 300, "calculators": 30})
    print("Scenario A (Heavy monitoring):", p_id, p_pcts)
    assert p_id == "field_inspector", f"Expected field_inspector, got {p_id}"
    
    # Scenario B: Heavy calculators
    p_id_b, p_pcts_b = compute_adaptive_persona({"monitoring": 3, "calculators": 25}, {"monitoring": 40, "calculators": 450})
    print("Scenario B (Heavy calculators):", p_id_b, p_pcts_b)
    assert p_id_b == "farm_planner", f"Expected farm_planner, got {p_id_b}"

    # Scenario C: Heavy analytics
    p_id_c, p_pcts_c = compute_adaptive_persona({"analytics": 22, "monitoring": 2}, {"analytics": 400, "monitoring": 30})
    print("Scenario C (Heavy analytics):", p_id_c, p_pcts_c)
    assert p_id_c == "data_analyst", f"Expected data_analyst, got {p_id_c}"

    # Scenario D: Balanced
    p_id_d, p_pcts_d = compute_adaptive_persona({"monitoring": 5, "calculators": 5, "analytics": 5}, {"monitoring": 60, "calculators": 60, "analytics": 60})
    print("Scenario D (Balanced):", p_id_d, p_pcts_d)
    assert p_id_d == "balanced_operator", f"Expected balanced_operator, got {p_id_d}"

    print("All persona classification scenarios passed!")

    # 2. Test Dynamic Next-Step Actions
    with patch("app.get_latest_sensor_dict", return_value={"temperature": 28.5, "ph": 8.9, "status": "Warning", "recorded_at": "2026-11-08 10:00:00"}):
        action_high_ph = get_adaptive_next_action("farm_planner")
        print("High pH action:", action_high_ph)
        assert action_high_ph["type"] == "warning"
        assert "Molasses" in action_high_ph["cta"] or "molasses" in action_high_ph["url"]

    with patch("app.get_latest_sensor_dict", return_value={"temperature": 28.5, "ph": 7.1, "status": "Warning", "recorded_at": "2026-11-08 10:00:00"}):
        action_low_ph = get_adaptive_next_action("field_inspector")
        print("Low pH action:", action_low_ph)
        assert action_low_ph["type"] == "warning"
        assert "Lime" in action_low_ph["cta"] or "lime" in action_low_ph["url"]

    with patch("app.get_latest_sensor_dict", return_value={"temperature": 29.0, "ph": 8.0, "status": "Optimal", "recorded_at": "2026-11-08 10:00:00"}):
        action_opt = get_adaptive_next_action("farm_planner")
        print("Optimal farm planner action:", action_opt)
        assert action_opt["type"] == "optimal"
        assert "Feed" in action_opt["cta"]

    print("Dynamic contextual next-step recommendations passed!")

    # 3. Test API Endpoints
    with app.test_client() as client:
        # GET profile
        res_prof = client.get("/api/adaptive/profile")
        assert res_prof.status_code == 200
        json_prof = res_prof.get_json()
        print("GET /api/adaptive/profile response persona:", json_prof["persona"]["id"])
        assert "persona" in json_prof
        assert "shortcuts" in json_prof["persona"]

        # POST sync
        sync_payload = {
            "interactions": {"calculators": 30, "monitoring": 4},
            "dwell": {"calculators": 500, "monitoring": 50},
            "device": {"type": "mobile_field", "is_touch": True},
            "preferences": {"auto_adapt": True, "sunlight_mode": "auto", "density": "comfort"}
        }
        res_sync = client.post("/api/adaptive/sync", json=sync_payload)
        assert res_sync.status_code == 200
        json_sync = res_sync.get_json()
        print("POST /api/adaptive/sync result persona:", json_sync["persona"]["id"])
        assert json_sync["persona"]["id"] == "farm_planner"

        # POST settings override
        res_sett = client.post("/api/adaptive/settings", json={"sunlight_mode": "always", "density": "compact"})
        assert res_sett.status_code == 200
        json_sett = res_sett.get_json()
        assert json_sett["preferences"]["sunlight_mode"] == "always"
        assert json_sett["preferences"]["density"] == "compact"
        print("POST /api/adaptive/settings updated preferences successfully!")

        # POST reset
        res_reset = client.post("/api/adaptive/reset")
        assert res_reset.status_code == 200
        json_reset = res_reset.get_json()
        assert json_reset["persona_id"] == "balanced_operator"
        print("POST /api/adaptive/reset restored defaults successfully!")

        # Verify pages serve adaptive.js
        for route in ["/", "/login", "/signup"]:
            r = client.get(route)
            assert r.status_code == 200
            if route == "/":
                assert "adaptive.js" in r.text
        print("Page template delivery verified successfully!")

    print("\nALL ADAPTIVE SYSTEM TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_adaptive_system()
