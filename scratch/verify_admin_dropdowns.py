import re

admin_files = [
    'templates/admin.html',
    'templates/admin_dashboard.html',
    'templates/admin_logs.html',
    'templates/admin_telemetry.html'
]

for filepath in admin_files:
    print(f"=== Checking {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Find all dropdown buttons
    btns = re.findall(r'<button\s+id="([^"]+)"\s+class="historical-toolbar-btn"[^>]*>', html)
    print(f"  Found {len(btns)} historical-toolbar-btn dropdown button(s):")
    for b in btns:
        print(f"    - #{b}")

    # Find all dropdown menus
    menus = re.findall(r'<div\s+id="([^"]+)"\s+class="(?:status|limit)-dropdown-menu"[^>]*>', html)
    print(f"  Found {len(menus)} dropdown menu(s):")
    for m in menus:
        print(f"    - #{m}")

    # Check for admindropdowns.js script include
    has_script = 'admindropdowns.js' in html
    print(f"  admindropdowns.js linked: {has_script}")

    # Check for css/style.css?v=3.3 link
    has_css_v = "v=3.3" in html
    print(f"  cache-busting v=3.3 present: {has_css_v}")
    print()
