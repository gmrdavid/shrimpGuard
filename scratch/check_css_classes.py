with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

keywords = ['.ammonia-', '.wqi-metric', '.metric-card', '.dashboard-input', '.tools-']
for kw in keywords:
    matches = [line for line in css.splitlines() if kw in line]
    print(f"{kw}: {len(matches)} matching lines")

