import sys
import os
import re
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Query

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, User

def test_signup():
    with app.test_client() as client:
        # GET /signup
        res = client.get("/signup", headers={"Host": "127.0.0.1:5000"})
        assert res.status_code == 200
        html = res.text
        match = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', html)
        assert match
        token = match.group(1)
        print("Signup CSRF token extracted:", token[:20] + "...")

        # POST /signup with isolated client
        isolated = app.test_client()
        with patch.object(Query, "first", return_value=None), \
             patch("app.db.session.add"), \
             patch("app.db.session.commit"), \
             patch("app.log_activity"):
            
            post_res = isolated.post(
                "/signup",
                data={
                    "csrf_token": token,
                    "user_name": "newclient",
                    "email": "client@gmail.com",
                    "password": "Password123!",
                    "confirm_password": "Password123!",
                },
                headers={"Host": "127.0.0.1:5000"},
                follow_redirects=False,
            )
            print("POST /signup status:", post_res.status_code)
            assert post_res.status_code == 302, f"Expected 302 redirect, got {post_res.status_code}"
            assert post_res.headers.get("Location") == "/login"
            print("Signup passed with 302 redirect to /login!")

        # Invalid token rejection
        fake_res = isolated.post(
            "/signup",
            data={
                "csrf_token": "fake_bad_token",
                "user_name": "newclient",
                "email": "client@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
            headers={"Host": "127.0.0.1:5000"},
        )
        assert "Your sign-up request expired. Please try again." in fake_res.text
        print("Signup fake token properly rejected!")

if __name__ == "__main__":
    test_signup()
