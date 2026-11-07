import re

with open('templates/devices.html', 'r', encoding='utf-8') as f:
    text = f.read()

inline_styles = re.findall(r'style=["\']([^"\']+)["\']', text)
print('--- Inline styles in devices.html ---')
for s in inline_styles:
    print(' ', s)

# Let's also print lines in devices.html where background, color, or card is defined
lines = text.splitlines()
print('\n--- Key lines in devices.html ---')
for i, l in enumerate(lines):
    if any(k in l.lower() for k in ['style=', 'class="device', 'class="status', 'table', 'badge', 'card']):
        print(f'{i+1}: {l.strip()[:100]}')
