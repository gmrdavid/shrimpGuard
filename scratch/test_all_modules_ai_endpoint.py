import sys
sys.path.insert(0, ".")
import json
from app import app

client = app.test_client()

with client.session_transaction() as sess:
    sess["user_id"] = 1
    sess["role"] = "Client"
    sess["email"] = "test@shrimpguard.com"

print("--- Testing /api/calculators/ai-insight for module='all' ---")
payload = {
    "module": "all",
    "data": {
        "feeding": {
            "area": 1000, "depth": 1.2, "density": 60, "survival": 85,
            "abw": 15.0, "biomass_kg": 765.0, "adjusted_feed_kg": 24.5, "temp": 29.5
        },
        "growth": {
            "doc": 90, "initial_stocking": 100000, "live_count": 85000,
            "survival_rate": 85.0, "fabw": 20.0, "adwg": 0.222, "fcr": 1.25, "k_factor": 0.85
        },
        "remediation": {
            "lime_kg": 54.0, "lime_ph": 7.2, "lime_target": 8.0,
            "molasses_kg": 18.4, "target_cn": 15, "aerator_hp": 2.0
        },
        "ammonia": {
            "tan": 0.80, "temp": 28.0, "ph": 7.60, "salinity": 20.0,
            "nh3_ppm": 0.0224, "factor": 0.0280
        },
        "co2": {
            "alkalinity": 140.0, "temp": 28.0, "ph": 7.60, "co2_ppm": 6.75, "factor": 0.0482
        }
    }
}

res = client.post("/api/calculators/ai-insight", json=payload)
print(f"Status Code: {res.status_code}")
assert res.status_code == 200, f"Expected 200, got {res.status_code}"

data = res.get_json()
print("Source:", data.get("source"))
print("Status:", data.get("status"))
print("Evaluation:", data.get("evaluation")[:140] + "...")
print("Action Items count:", len(data.get("action_items", [])))
for i, item in enumerate(data.get("action_items", [])):
    print(f"  {i+1}. {item}")

print("\n>>> Module 'all' Master Assessment test PASSED! <<<")

