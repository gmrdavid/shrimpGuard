import sys
sys.path.insert(0, '.')
from app import app, db, User

print("=== STARTING COMPREHENSIVE CLIENT TEST SUITE ===")
test_client = app.test_client()

with test_client.session_transaction() as sess:
    sess["user_id"] = "rio@gmail.com"
    sess["user_role"] = "Client"
    sess["user_name"] = "Rio"

routes_to_test = [
    ("/dashboard", 200, b"ShrimpGuard Dashboard"),
    ("/monitoring", 200, b"Real-time Monitoring"),
    ("/historical", 200, b"Historical Data"),
    ("/analytics", 200, b"Analytics &amp; Reports"),
    ("/alerts", 200, b"Alerts and Notifications"),
    ("/calculators", 200, b"Aquaculture Tools &amp; Calculators"),
    ("/aquaculture-tools", 200, b"Aquaculture Tools &amp; Calculators"),
    ("/settings", 200, b"Settings"),
    ("/historical/export", 200, None),
    ("/api/readings/latest", 200, None),
    ("/api/readings/history", 200, None),
    ("/api/alerts", 200, None),
    ("/api/wqi/calculate?temperature=29.5&ph=8.0", 200, None),
    ("/api/ammonia/calculate?temperature=28&ph=7.6&tan=0.8", 200, None),
]

all_passed = True
for path, expected_status, expected_text in routes_to_test:
    res = test_client.get(path)
    status_ok = res.status_code == expected_status
    text_ok = expected_text in res.data if expected_text else True
    
    if status_ok and text_ok:
        print(f"  [PASS] {path} -> HTTP {res.status_code} (length: {len(res.data)})")
    else:
        all_passed = False
        print(f"  [FAIL] {path} -> HTTP {res.status_code} (expected {expected_status}), text_ok={text_ok}")
        if not status_ok:
            print("         Data preview:", res.data[:200])

# Check that every client HTML page contains the new Aquaculture Tools navigation item
html_pages = ["/dashboard", "/monitoring", "/historical", "/analytics", "/alerts", "/calculators", "/settings"]
print("\n=== VERIFYING AQUACULTURE TOOLS NAV LINK ACROSS ALL CLIENT PAGES ===")
for p in html_pages:
    res = test_client.get(p)
    has_nav = b'href="/calculators"' in res.data
    has_title = b"Aquaculture Tools" in res.data
    if has_nav and has_title:
        print(f"  [PASS] {p} contains /calculators and 'Aquaculture Tools'")
    else:
        all_passed = False
        print(f"  [FAIL] {p} missing /calculators link!")

if all_passed:
    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! CLIENT SIDE IS HEALTHY & COMPLETE! <<<")
else:
    print("\n>>> SOME TESTS FAILED! <<<")

