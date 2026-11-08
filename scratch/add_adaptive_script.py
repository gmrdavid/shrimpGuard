import os

templates = [
    "admin.html",
    "admin_dashboard.html",
    "admin_logs.html",
    "admin_telemetry.html",
    "alerts.html",
    "analytics.html",
    "calculators.html",
    "dashboard.html",
    "devices.html",
    "historical.html",
    "monitoring.html",
    "settings.html",
]

script_tag = '<script src="{{ url_for(\'static\', filename=\'js/adaptive.js\') }}"></script>'

for t in templates:
    path = os.path.join("templates", t)
    if not os.path.exists(path):
        continue
    content = open(path, encoding="utf-8").read()
    if "adaptive.js" in content:
        print(f"Skipping {t}, already has adaptive.js")
        continue

    # Insert after notifications.js
    notif_target = '<script src="{{ url_for(\'static\', filename=\'js/notifications.js\') }}"></script>'
    if notif_target in content:
        new_content = content.replace(notif_target, notif_target + "\n" + script_tag)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new_content)
        print(f"Added adaptive.js to {t}")
    else:
        print(f"Warning: notifications.js not found in {t}")

# Handle landing.html
landing_path = os.path.join("templates", "landing.html")
landing_content = open(landing_path, encoding="utf-8").read()
if "adaptive.js" not in landing_content:
    landing_new = landing_content.replace("</body>", f"{script_tag}\n</body>")
    with open(landing_path, "w", encoding="utf-8") as fh:
        fh.write(landing_new)
    print("Added adaptive.js to landing.html")
