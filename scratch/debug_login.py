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
print("Extracted CSRF token:", token)

login_res = test_client.post("/login", data={
    "email": "rio@gmail.com",
    "password": "rio",
    "csrf_token": token
}, follow_redirects=False)

print("POST /login status:", login_res.status_code)
print("POST /login headers Location:", login_res.headers.get("Location"))
print("POST /login data snippet:", login_res.data[:300])

