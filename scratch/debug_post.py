import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

with app.test_client() as client:
    res = client.get("/login", headers={"Host": "127.0.0.1:5000"})
    token = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', res.text).group(1)
    
    # POST with empty username
    post_res = client.post("/login", data={"csrf_token": token, "user_name": "", "password": ""}, headers={"Host": "127.0.0.1:5000"})
    print("Empty user POST status:", post_res.status_code)
    for line in post_res.text.splitlines():
        if "login-alert" in line or "Enter your" in line or "error" in line.lower():
            print("Line:", line.strip())
