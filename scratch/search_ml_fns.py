import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

for match in re.finditer(r'def\s+.*?(?:wqi|quality|classify|decision|predict|status).*?\(.*?\):', text, re.DOTALL):
    print(match.group(0))

