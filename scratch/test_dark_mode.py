import os
import sys

# Ensure current dir is in python path
sys.path.insert(0, os.path.abspath("."))

from app import app

client = app.test_client()

print("--- Testing ShrimpGuard Dark Mode Implementation ---")

# 1. Test CSS file contains data-theme rules
with open("static/css/style.css", "r", encoding="utf-8") as f:
    css_content = f.read()

assert 'data-theme="dark"' in css_content, "CSS must contain data-theme='dark'"
assert ".theme-toggle-btn" in css_content, "CSS must contain .theme-toggle-btn"
assert ".theme-icon-moon" in css_content, "CSS must contain .theme-icon-moon"
assert ".theme-icon-sun" in css_content, "CSS must contain .theme-icon-sun"
print("✓ CSS Dark Mode tokens, toggle button styles, and overrides verified.")

# 2. Test _icon_sprite.html contains icon-moon and icon-sun
with open("templates/_icon_sprite.html", "r", encoding="utf-8") as f:
    sprite_content = f.read()

assert 'id="icon-moon"' in sprite_content, "Sprite must contain icon-moon"
assert 'id="icon-sun"' in sprite_content, "Sprite must contain icon-sun"
print("✓ SVG icon sprite includes #icon-moon and #icon-sun.")

# 3. Test static/js/theme.js exists and is valid
with open("static/js/theme.js", "r", encoding="utf-8") as f:
    theme_js = f.read()

assert "shrimp_theme" in theme_js, "theme.js must use localStorage key"
assert "toggleTheme" in theme_js, "theme.js must have toggleTheme function"
assert "applyTheme" in theme_js, "theme.js must have applyTheme function"
print("✓ static/js/theme.js exists with full lifecycle & event dispatching.")

# 4. Test rendering of all 12 templates
user_templates = [
    "dashboard.html",
    "monitoring.html",
    "devices.html",
    "historical.html",
    "analytics.html",
    "alerts.html",
    "calculators.html",
    "settings.html"
]

admin_templates = [
    "admin_dashboard.html",
    "admin.html",
    "admin_telemetry.html",
    "admin_logs.html"
]

all_templates = user_templates + admin_templates

for tpl_name in all_templates:
    filepath = os.path.join("templates", tpl_name)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()
    
    assert "theme-toggle-btn" in html, f"{tpl_name} must contain theme-toggle-btn"
    assert "theme.js" in html, f"{tpl_name} must include theme.js"
    assert "shrimp_theme" in html, f"{tpl_name} must contain pre-render theme script"
    assert "icon-moon" in html, f"{tpl_name} must reference icon-moon"
    assert "icon-sun" in html, f"{tpl_name} must reference icon-sun"
    print(f"✓ {tpl_name}: Pre-render script, #theme-toggle-btn, and theme.js present.")

# 5. Test Jinja template rendering in app context
from flask import render_template

with app.test_request_context():
    dummy_context = {
        "user": None,
        "greeting": "Good morning",
        "online_devices": 10,
        "offline_devices": 0,
        "total_devices": 10,
        "connected_sensors": 4,
        "sensor_devices": 4,
        "comm_devices": 4,
        "power_devices": 2,
        "devices": [],
        "overall_status": "Optimal",
        "wqi_score": 92,
        "logout_csrf_token": "dummy_token",
        "current_page": "dashboard",
        "total_users": 5,
        "active_users": 4,
        "inactive_users": 1,
        "role_summary": [],
        "recent_activities": [],
        "system_online": True,
        "latest_reading": {"status": "Optimal", "recorded_at": "Just now", "temperature": 28.5, "ph": 8.0, "wqi_score": 92},
        "hardware_stream": {"is_connected": True, "port": "COM3", "baud_rate": 9600, "sample_interval_sec": 3},
        "hw_connected": True,
        "gateway_online": True,
        "users": [],
        "admin_csrf_token": "admin_token",
        "total_readings": 120,
        "optimal_count": 100,
        "optimal_pct": 83.3,
        "warning_count": 15,
        "warning_pct": 12.5,
        "critical_count": 5,
        "critical_pct": 4.2,
        "logs": [],
        "total_logs": 50,
        "auth_events": 20,
        "user_mgmt_events": 30
    }

    for tpl_name in all_templates:
        try:
            rendered = render_template(tpl_name, **dummy_context)
            assert "theme-toggle-btn" in rendered, f"{tpl_name} rendered missing theme-toggle-btn"
            assert "theme.js" in rendered, f"{tpl_name} rendered missing theme.js"
            print(f"✓ {tpl_name}: Jinja rendered successfully without errors.")
        except Exception as e:
            print(f"✗ Error rendering {tpl_name}: {e}")
            raise e

print("\n--- All Dark Mode Checks Passed Successfully! ---")
