import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

matches = re.findall(r'(\.[\w-]+nav[^{]*\{[^}]*\})', css)
print(f"Found {len(matches)} nav CSS rules:")
for m in matches[:10]:
    print(m[:100] + "...")

