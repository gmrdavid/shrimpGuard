import os
import re

for f in sorted(os.listdir("templates")):
    if f.endswith(".html") and not f.startswith("_"):
        text = open(os.path.join("templates", f), encoding="utf-8").read()
        scripts = re.findall(r'<script\s+[^>]*src=["\']([^"\']+)["\']', text)
        print(f"{f}: {scripts}")
