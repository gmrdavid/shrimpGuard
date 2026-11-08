import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, session
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import secrets
import hmac

class AdaptiveSessionInterface(SecureCookieSessionInterface):
    def _is_secure_context(self) -> bool:
        if not request:
            return False
        if request.is_secure:
            return True
        proto = request.headers.get("X-Forwarded-Proto", "").strip().lower()
        if proto == "https":
            return True
        host = (request.host or "").split(":")[0].strip().lower()
        return host in {"localhost", "127.0.0.1", "::1", "testserver"}

    def get_cookie_secure(self, app: Flask) -> bool:
        configured = app.config.get("SESSION_COOKIE_SECURE_OVERRIDE")
        if configured is not None:
            return bool(configured)
        return self._is_secure_context()

    def get_cookie_samesite(self, app: Flask) -> str | None:
        configured = app.config.get("SESSION_COOKIE_SAMESITE_OVERRIDE")
        if configured is not None:
            return configured
        if self._is_secure_context():
            return "None"
        return "Lax"

    def get_cookie_partitioned(self, app: Flask) -> bool:
        configured = app.config.get("SESSION_COOKIE_PARTITIONED_OVERRIDE")
        if configured is not None:
            return bool(configured)
        return self._is_secure_context()


def generate_timed_csrf_token(secret_key: str, purpose: str) -> str:
    s = URLSafeTimedSerializer(secret_key, salt=f"shrimpguard-csrf-{purpose}")
    return s.dumps(purpose)

def verify_timed_csrf_token(secret_key: str, token: str, purpose: str, max_age: int = 3600) -> bool:
    if not token:
        return False
    s = URLSafeTimedSerializer(secret_key, salt=f"shrimpguard-csrf-{purpose}")
    try:
        data = s.loads(token, max_age=max_age)
        return data == purpose
    except (BadSignature, SignatureExpired):
        return False


# Let's test with real app
from app import app, db, User

# Temporarily assign adaptive session interface
app.session_interface = AdaptiveSessionInterface()

with app.test_client() as client:
    # 1. GET /login from localhost
    res_get = client.get("/login", headers={"Host": "127.0.0.1:5000"})
    print("GET /login status:", res_get.status_code)
    print("GET /login Set-Cookie:", res_get.headers.get("Set-Cookie"))
    
    # Check that cookie has Secure; SameSite=None; Partitioned
    cookie = res_get.headers.get("Set-Cookie", "")
    assert "Secure" in cookie
    assert "SameSite=None" in cookie
    assert "Partitioned" in cookie
    print("Assertion passed: Cookie has Secure; SameSite=None; Partitioned on 127.0.0.1")

    # 2. Test timed token verification directly
    token = generate_timed_csrf_token(app.secret_key, "login")
    assert verify_timed_csrf_token(app.secret_key, token, "login")
    assert not verify_timed_csrf_token(app.secret_key, "fake_token", "login")
    assert not verify_timed_csrf_token(app.secret_key, token, "signup")
    print("Assertion passed: Timed CSRF tokens generate and verify properly.")
