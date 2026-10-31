import glob
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
    navs = re.findall(r'<nav[^>]*>.*?</nav>', content, re.DOTALL)
    print(f"\n=== {path} ===")
    print(f"Total <nav> elements: {len(navs)}")
    for i, n in enumerate(navs):
        first_line = n.split('\n')[0]
        links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', n, re.DOTALL)
        clean_links = [(h, re.sub(r'<[^>]+>', '', t).strip()) for h, t in links]
        print(f"  Nav #{i+1} opening: {first_line}")
        print(f"    Links: {clean_links}")
