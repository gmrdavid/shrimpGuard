import re

files = [
    'templates/dashboard.html',
    'templates/monitoring.html',
    'templates/historical.html',
    'templates/analytics.html',
    'templates/alerts.html',
    'templates/settings.html'
]

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    aside = re.search(r'<aside\s+class="([^"]+)"', content)
    nav = re.search(r'<nav\s+class="([^"]+)"', content)
    header = re.search(r'<header\s+class="([^"]+)"', content)
    print(f"{path}:")
    print(f"  aside: {aside.group(1) if aside else 'None'}")
    print(f"  nav:   {nav.group(1) if nav else 'None'}")
    print(f"  header:{header.group(1) if header else 'None'}")

