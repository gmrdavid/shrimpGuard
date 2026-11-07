import glob
import re

found = []
for tpl in glob.glob("templates/*.html"):
    with open(tpl, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines, 1):
        if "style=" in line and ("{%" in line or "{{" in line):
            found.append((tpl, i, line.strip()))

print(f"Total style lines with Jinja: {len(found)}")
for tpl, i, line in found:
    print(f"{tpl}:{i}: {line}")
