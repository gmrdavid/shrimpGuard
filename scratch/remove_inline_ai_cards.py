import re

with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

def normalize(s):
    return s.replace("\r\n", "\n")

html_norm = normalize(html)

# Remove the 5 inline ai cards
pattern = r"\s*<!-- AI DECISION SUPPORT CARD \([A-Z0-9_]+\) -->\s*<div class=\"tools-ai-card\" id=\"ai-card-[a-z0-9_]+\"[\s\S]*?</div>\s*</div>"
matches = list(re.finditer(pattern, html_norm))
print(f"Found {len(matches)} inline AI cards to remove.")

html_norm_cleaned = re.sub(pattern, "", html_norm)

with open("templates/calculators.html", "w", encoding="utf-8") as f:
    f.write(html_norm_cleaned)

print("Removed inline AI cards successfully!")

