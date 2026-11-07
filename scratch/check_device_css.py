import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Find rules for .devices-page or device-cell or category or status-ratio
for m in re.finditer(r'([^{}]*?(?:device-cell|devices-page|category-item|status-ratio|category-name)[^{}]*?)\{([^}]*)\}', css):
    sel = m.group(1).strip()
    body = m.group(2).strip()
    print('SELECTOR:', sel)
    print('BODY:', body)
    print('---')
