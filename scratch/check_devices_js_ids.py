import re

with open('static/js/devices.js', 'r', encoding='utf-8') as f:
    js = f.read()

with open('templates/devices.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find getElementById in js
get_ids = re.findall(r'document\.getElementById\(["\']([^"\']+)["\']\)', js)
print(f"Total getElementById calls in devices.js: {len(get_ids)}")

html_ids = set(re.findall(r'id=["\']([^"\']+)["\']', html))

missing = []
for gid in set(get_ids):
    if gid not in html_ids:
        missing.append(gid)

print("IDs in devices.js NOT found in devices.html:")
for m in sorted(missing):
    print(f"  - {m}")
