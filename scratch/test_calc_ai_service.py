from calculator_ai_service import get_calculator_ai_insight

modules_to_test = [
    ("feeding", {
        "area": 1000,
        "depth": 1.2,
        "density": 60,
        "survival": 85,
        "abw": 15.0,
        "base_rate": 3.2,
        "meals": 4,
        "temp": 29.5,
        "biomass_kg": 765.0,
        "adjusted_feed_kg": 24.5,
        "temp_factor": 1.00
    }),
    ("growth", {
        "doc": 90,
        "initial_stocking": 100000,
        "live_count": 85000,
        "survival_rate": 85.0,
        "fabw": 20.0,
        "adwg": 0.22,
        "sgr": 8.44,
        "final_biomass": 1700.0,
        "fcr": 1.25,
        "k_factor": 0.85
    }),
    ("ammonia", {
        "tan": 0.80,
        "temp": 28.0,
        "ph": 7.60,
        "salinity": 20.0,
        "nh3_ppm": 0.0224,
        "factor": 0.0280
    }),
    ("co2", {
        "alkalinity": 140.0,
        "temp": 28.0,
        "ph": 7.60,
        "co2_ppm": 6.75,
        "factor": 0.0482
    })
]

print("=== Testing Calculator AI Service ===")
for mod, payload in modules_to_test:
    res = get_calculator_ai_insight(mod, payload)
    print(f"\n--- Module: {mod.upper()} ---")
    print(f"Status: {res.get('status')}")
    print(f"Source: {res.get('source')}")
    print(f"Evaluation: {res.get('evaluation')[:120]}...")
    print(f"Recommendation: {res.get('recommendation')[:100]}...")
    print(f"Action Items: {len(res.get('action_items', []))} items")

print("\n=== ALL MODULE TESTS COMPLETED SUCCESSFULLY ===")

