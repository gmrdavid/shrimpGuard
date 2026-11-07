import re

with open('templates/devices.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    for m in re.finditer(r'style="([^"]*)"', line):
        print(f"Line {i}: {m.group(1)}")
