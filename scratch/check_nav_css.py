with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

import re
matches = re.findall(r'(\.[a-z]+-nav\s*\{[^}]+\})', css)
for m in matches[:10]:
    print(m)

