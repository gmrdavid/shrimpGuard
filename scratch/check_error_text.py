import sys
sys.path.insert(0, '.')
import re
from app import app, db, User

test_client = app.test_client()

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
idx = html2.find("login-notice-error")
print(html2[idx:idx+400])

