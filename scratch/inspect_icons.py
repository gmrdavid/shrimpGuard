import re

with open('templates/_icon_sprite.html', 'r', encoding='utf-8') as f:
    text = f.read()

symbols = re.findall(r'<symbol[^>]+id="([^"]+)"', text)
print("Icons in sprite:")
for s in symbols:
    print(" -", s)
