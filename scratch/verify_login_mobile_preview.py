import sys
import os
import re
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Query

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, User

def run_tests():
    print("=== Running Comprehensive Mobile Preview & Authentication Tests ===")
    
    with app.test_client() as client:
        # 1. GET /login on 127.0.0.1
        res = client.get("/login", headers={"Host": "127.0.0.1:5000"})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        
        cookie = res.headers.get("Set-Cookie", "")
        print("1. GET /login Cookie Header:", cookie)
        assert "SameSite=None" in cookie, "SameSite=None missing on localhost"
        assert "Secure" in cookie, "Secure flag missing on localhost"
        assert "Partitioned" in cookie, "Partitioned attribute missing on localhost"
        assert "HttpOnly" in cookie, "HttpOnly missing"
        
        # Extract CSRF token from HTML
        html = res.text
        match = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', html)
        assert match, "csrf_token input not found in login.html"
        csrf_token = match.group(1)
        print("Extracted CSRF token from login HTML:", csrf_token[:20] + "...")
        assert len(csrf_token) > 20, "CSRF token is suspiciously short"

        # Mock user
        mock_user = MagicMock()
        mock_user.id = "user@example.com"
        mock_user.email = "user@example.com"
        mock_user.user_name = "testuser"
        mock_user.name = "Test User"
        mock_user.role = "Client"
        mock_user.check_password.return_value = True
        mock_user.password_needs_rehash.return_value = False

        # 2. Simulate Mobile Preview Webview iframe:
        # Client sends POST with CSRF token and credentials, but without any prior session cookie.
        isolated_client = app.test_client()
        
        with patch.object(Query, "filter") as mock_filter, \
             patch("app.db.session.commit") as mock_commit, \
             patch("app.log_activity") as mock_log:
            
            mock_filter.return_value.first.return_value = mock_user

            post_res = isolated_client.post(
                "/login",
                data={
                    "csrf_token": csrf_token,
                    "user_name": "testuser",
                    "password": "valid_password",
                },
                headers={"Host": "127.0.0.1:5000"},
                follow_redirects=False,
            )
            
            print("2. POST /login (no initial cookie) status:", post_res.status_code)
            if post_res.status_code != 302:
                for line in post_res.text.splitlines():
                    if "login-notice" in line or "span" in line.lower():
                        print("Notice line:", line.strip())
            assert post_res.status_code == 302, f"Expected 302 redirect, got {post_res.status_code}"
            assert post_res.headers.get("Location") == "/dashboard", f"Expected /dashboard, got {post_res.headers.get('Location')}"
            
            auth_cookie = post_res.headers.get("Set-Cookie", "")
            print("Authenticated Set-Cookie Header:", auth_cookie)
            assert "SameSite=None" in auth_cookie, "SameSite=None missing on auth cookie"
            assert "Secure" in auth_cookie, "Secure missing on auth cookie"
            assert "Partitioned" in auth_cookie, "Partitioned missing on auth cookie"
            print("3. Authenticated session successfully created without prior cookie!")

        # 3. Test invalid CSRF token rejection
        attacker_client = app.test_client()
        attacker_res = attacker_client.post(
            "/login",
            data={
                "csrf_token": "malicious_fake_token_12345",
                "user_name": "testuser",
                "password": "valid_password",
            },
            headers={"Host": "127.0.0.1:5000"},
        )
        assert attacker_res.status_code == 200, f"Expected 200 re-render with error, got {attacker_res.status_code}"
        assert "Your sign-in request expired. Please try again." in attacker_res.text, "Expired message missing on fake token"
        print("4. CSRF protection verified: Fake token was successfully rejected!")

        # 4. Test LAN IP cookie formatting (e.g. 192.168.1.50)
        lan_res = client.get("/login", headers={"Host": "192.168.1.50:5000"})
        lan_cookie = lan_res.headers.get("Set-Cookie", "")
        print("5. LAN IP Set-Cookie Header:", lan_cookie)
        assert "SameSite=Lax" in lan_cookie, "Expected SameSite=Lax for non-localhost HTTP"
        assert "Secure" not in lan_cookie, "Secure should NOT be set on plain HTTP LAN IP"
        print("6. LAN IP fallback verified successfully!")

    print("\nALL TESTS PASSED SUCCESSFULLY! No regressions detected.")

if __name__ == "__main__":
    run_tests()
