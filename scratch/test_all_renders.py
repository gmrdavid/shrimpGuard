# -*- coding: utf-8 -*-
import jinja2

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class MockUser:
    email = "test@shrimpguard.com"
    first_name = "Aquaculture"
    last_name = "Specialist"
    user_name = "Aquaculture Specialist"
    role = "Client"
    ntfy_topic = "sg-pond-test"

def mock_url_for(endpoint, **values):
    return f"/{endpoint}/" + "/".join(str(v) for v in values.values())

# 1. Test calculators.html
template_calc = env.get_template('calculators.html')
rendered_calc = template_calc.render(user=MockUser(), url_for=mock_url_for, get_flashed_messages=lambda **kw: [])
assert "Computed Performance Metrics" in rendered_calc
assert "Water Remediation" in rendered_calc
assert "tools-icon-remediation" in rendered_calc
assert "tools-remediation-section" in rendered_calc
assert "growth-trend-graph-modal" in rendered_calc
assert "btn-open-growth-chart" in rendered_calc
print("calculators.html rendered cleanly!")

# 2. Test historical.html
template_hist = env.get_template('historical.html')
rendered_hist = template_hist.render(user=MockUser(), url_for=mock_url_for, get_flashed_messages=lambda **kw: [])
assert "history-export-button" not in rendered_hist, "history-export-button should be removed from chart"
assert "history-interval" not in rendered_hist, "history-interval should be removed from filter form"
assert "table-export-button" in rendered_hist, "table-export-button should remain in data table"
print("historical.html rendered cleanly!")

# 3. Test alerts.html
template_alerts = env.get_template('alerts.html')
rendered_alerts = template_alerts.render(user=MockUser(), url_for=mock_url_for, get_flashed_messages=lambda **kw: [])
assert "mark-all-read-btn" not in rendered_alerts, "mark-all-read-btn should be removed"
assert "unread-notifications-count" in rendered_alerts, "unread-notifications-count should remain"
print("alerts.html rendered cleanly!")

# 4. Test settings.html
template_settings = env.get_template('settings.html')
rendered_settings = template_settings.render(user=MockUser(), url_for=mock_url_for, settings_csrf_token="dummy", get_flashed_messages=lambda **kw: [])
assert "icon-user" in rendered_settings, "icon-user should be used for Profile Information"
assert "Profile Information" in rendered_settings
assert "Password &amp; Security" in rendered_settings
print("settings.html rendered cleanly!")

# 5. Test landing.html
template_landing = env.get_template('landing.html')
rendered_landing = template_landing.render(url_for=mock_url_for, current_year=2026)
assert "ShrimpGuard" in rendered_landing
assert "Penaeus vannamei" in rendered_landing
assert "Google Gemini" in rendered_landing
assert "landing-stats-strip" in rendered_landing
assert "landing-workflow-section" in rendered_landing
assert "landing-calc-section" in rendered_landing
assert "landing-ai-section" in rendered_landing
print("landing.html rendered cleanly!")

print("All Jinja2 rendering tests passed with flying colors!")


