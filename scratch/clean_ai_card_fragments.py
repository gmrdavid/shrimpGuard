import re

with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

def normalize(s):
    return s.replace("\r\n", "\n")

html_norm = normalize(html)

fragment_pattern = r"\s*<div class=\"ai-header-actions\">[\s\S]*?<span id=\"ai-source-[a-z0-9_]+\" class=\"ai-source-stamp\">[\s\S]*?</div>\s*</div>"

matches = list(re.finditer(fragment_pattern, html_norm))
print(f"Found {len(matches)} card fragments to remove.")

html_clean = re.sub(fragment_pattern, "", html_norm)

with open("templates/calculators.html", "w", encoding="utf-8") as f:
    f.write(html_clean)

print("Cleaned all fragments successfully!")

