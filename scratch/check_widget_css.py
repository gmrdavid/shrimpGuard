import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

for m in re.finditer(r'([^{}]*?(?:device-status-widget|device-category-widget|status-ratio-number|category-name|category-meta)[^{}]*?)\{([^}]*)\}', css):
    sel = m.group(1).strip()
    body = m.group(2).strip()
    print('SELECTOR:', sel)
    print('BODY:', body)
    print('---')
