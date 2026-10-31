import os, re

files = ['static/js/historical.js', 'static/js/analytics.js', 'static/js/alerts.js', 'static/js/settings.js', 'static/js/notifications.js']

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    functions = re.findall(r'function\s+([a-zA-Z0-9_]+)', text)
    print(f"\n{path} (len: {len(text)}):")
    print("  Functions:", functions[:10], f"(total: {len(functions)})")

