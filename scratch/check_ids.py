import re

with open('templates/devices.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    m = re.findall(r'id=["\']([^"\']+)["\']', line)
    for match in m:
        if '{' in match or '}' in match:
            print(f"Line {i}: id='{match}'\n  {line.strip()}")
