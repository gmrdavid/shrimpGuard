import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'animation' in line and not line.strip().startswith('/*'):
        print(f"Line {i}: {line.strip()}")
