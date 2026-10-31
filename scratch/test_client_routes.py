import sys
sys.path.insert(0, '.')
import re
from app import app, db, User

test_client = app.test_client()

# 1. Login as rio@gmail.com
login_page = test_client.get("/login")
html = login_page.data.decode('utf-8')
token_match = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', html)
token = token_match.group(1) if token_match else ""

login_res = test_client.post("/login", data={
    "user_name": "rio@gmail.com",
    "password": "rio",
    "csrf_token": token
}, follow_redirects=True)

print("Login status:", login_res.status_code)
print("After login page contains 'Dashboard':", b'Dashboard' in login_res.data)

routes = [
    "/dashboard",
    "/monitoring",
    "/historical",
    "/analytics",
    "/alerts",
    "/settings",
    "/api/readings/latest",
    "/api/readings/history?limit=10",
    "/api/alerts",
    "/api/wqi/calculate?temperature=29&ph=8.0",
    "/api/ammonia/calculate?temperature=28&ph=7.6&tan=0.8"
]

print("\nTesting routes with Flask test client:")
for r in routes:
    try:
        res = test_client.get(r)
        print(f"  {r} -> HTTP {res.status_code} (length: {len(res.data)})")
    except Exception as e:
        print(f"  {r} -> EXCEPTION: {e}")
