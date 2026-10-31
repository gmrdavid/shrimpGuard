import re

files = [
    'templates/dashboard.html',
    'templates/monitoring.html',
    'templates/historical.html',
    'templates/analytics.html',
    'templates/alerts.html',
    'templates/settings.html'
]

print("=== CHECKING TEMPLATE INCLUDES & SCRIPTS ===")
for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    title = re.search(r'<title>(.*?)</title>', c)
    nav_links = re.findall(r'<a\s+href="([^"]+)"(?:\s+class="([^"]*)")?[^>]*>\s*(?:<svg.*?</svg>)?\s*<span>([^<]+)</span>', c)
    print(f"\n{path} (Title: {title.group(1) if title else 'None'}):")
    for href, cls, label in nav_links:
        print(f"  [{label.strip()}] -> {href} ({cls})")

