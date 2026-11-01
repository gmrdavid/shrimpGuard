import sys
sys.path.insert(0, ".")
import json
from app import app

client = app.test_client()

print("--- Testing /api/calculators/ai-insight without session (should 401) ---")
res = client.post("/api/calculators/ai-insight", json={"module": "feeding", "data": {}})
print("Status code:", res.status_code)
assert res.status_code == 401, f"Expected 401, got {res.status_code}"

print("\n--- Testing /api/calculators/ai-insight with logged in user ---")
with client.session_transaction() as sess:
    sess["user_id"] = 1
    sess["role"] = "Client"
    sess["email"] = "test@shrimpguard.com"

modules = ["feeding", "growth", "remediation", "ammonia", "co2"]
for mod in modules:
    res = client.post("/api/calculators/ai-insight", json={
        "module": mod,
        "data": {
            "temp": 29.0,
            "ph": 7.8,
            "salinity": 20.0,
            "tan": 0.5,
            "alkalinity": 130.0,
            "biomass_kg": 800.0,
            "adjusted_feed_kg": 25.0
        }
    })
    print(f"Module '{mod}': HTTP {res.status_code}")
    assert res.status_code == 200, f"Expected 200 for {mod}, got {res.status_code}"
    data = res.get_json()
    assert "evaluation" in data, f"'evaluation' missing in response for {mod}"
    assert "action_items" in data, f"'action_items' missing in response for {mod}"
    assert "source" in data, f"'source' missing in response for {mod}"
    print(f"  Source: {data['source']}")
    print(f"  Status: {data['status']}")
    print(f"  Actions count: {len(data['action_items'])}")

print("\n>>> ALL ENDPOINT TESTS PASSED CLEANLY! <<<")
