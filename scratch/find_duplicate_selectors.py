import re
from collections import defaultdict

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

# Strip comments
clean = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

# Let's find selectors and their line numbers
lines = text.split('\n')
# We can search for selectors
selector_lines = defaultdict(list)

# Simple selector parser
for i, line in enumerate(lines, 1):
    s = line.strip()
    if s.endswith('{') and not s.startswith('@'):
        sel = s[:-1].strip()
        selector_lines[sel].append(i)

duplicates = {k: v for k, v in selector_lines.items() if len(v) > 1}
print(f"Total duplicate selector lines: {len(duplicates)}")
# Filter for exact selector duplicates especially in the recent additions (> 23000)
recent_dupes = {k: v for k, v in duplicates.items() if any(line > 23000 for line in v)}
print(f"Recent duplicate selectors (touching > 23000): {len(recent_dupes)}")
for k, v in list(recent_dupes.items())[:30]:
    print(f"[{k}] appears on lines: {v}")
