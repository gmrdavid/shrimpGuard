import re

with open('templates/devices.html', encoding='utf-8') as f:
    dev_content = f.read()

with open('templates/_icon_sprite.html', encoding='utf-8') as f:
    sprite_content = f.read()

icon_uses = set(re.findall(r'href="#([^"]+)"', dev_content))
sprite_symbols = set(re.findall(r'id="([^"]+)"', sprite_content))

missing_icons = [icon for icon in icon_uses if icon not in sprite_symbols]
print("Missing icon symbols in _icon_sprite.html:")
for m in missing_icons:
    print(" -", m)

print("\nAll icon uses found in devices.html:", sorted(list(icon_uses)))
