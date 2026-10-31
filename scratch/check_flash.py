with open('scratch/debug_login.py', 'r') as f:
    pass

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
    "email": "rio@gmail.com",
    "password": "rio",
    "csrf_token": token
}, follow_redirects=False)

html2 = login_res.data.decode('utf-8')
flashes = re.findall(r'class="[^"]*login-message[^"]*"[^>]*>(.*?)<', html2)
if not flashes:
    flashes = re.findall(r'<p[^>]*class="[^"]*error[^"]*"[^>]*>(.*?)</p>', html2)
print("Flashes found:", flashes)
for line in html2.splitlines():
    if "error" in line.lower() or "invalid" in line.lower() or "alert" in line.lower():
        print("  ->", line.strip())

