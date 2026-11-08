import re

text = open("templates/_icon_sprite.html", encoding="utf-8").read()
ids = re.findall(r'id=["\']([^"\']+)["\']', text)
print("Icons found:", len(ids), ids)
