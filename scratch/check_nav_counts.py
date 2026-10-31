with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

for name in ['dashboard-nav', 'monitoring-nav', 'historical-nav', 'analytics-nav', 'alerts-nav', 'settings-nav']:
    count = css.count(name)
    print(f"{name}: {count} occurrences in style.css")

