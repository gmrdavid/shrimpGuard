import re
from collections import defaultdict

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
keyframes = defaultdict(list)
for i, line in enumerate(lines, 1):
    m = re.search(r'@keyframes\s+([a-zA-Z0-9_-]+)', line)
    if m:
        keyframes[m.group(1)].append(i)

print(f"Total keyframes: {len(keyframes)}")
for name, lnums in keyframes.items():
    if len(lnums) > 1:
        print(f"Duplicate @keyframes '{name}' on lines: {lnums}")
