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
        c = f.read()
    nav_match = re.search(r'<nav[^>]*aria-label="Main navigation"[^>]*>(.*?)</nav>', c, re.DOTALL)
    print(f"\n=== {path} ===")
    if nav_match:
        nav_html = nav_match.group(1)
        links = re.findall(r'<a\s+[^>]*href="([^"]+)"[^>]*>.*?<span>(.*?)</span>.*?</a>', nav_html, re.DOTALL)
        for href, title in links:
            print(f"  {title.strip()} -> {href}")
    else:
        print("  NO Main navigation nav found!")

