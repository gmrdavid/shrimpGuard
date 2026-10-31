import re

with open('templates/calculators.html', 'r', encoding='utf-8') as f:
    text = f.read()

icons = re.findall(r'href=["\']#(icon-[^"\']+)["\']', text)
print("Icons referenced in calculators.html:", set(icons))
