import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

# Strip comments
clean = re.sub(r'/\*.*?\*/', ' ', text, flags=re.DOTALL)

# Find all blocks: selector { ... }
# Notice that nested blocks (like @media { sel { ... } }) exist.
# Let's tokenize by { and }
tokens = []
i = 0
n = len(clean)
buf = []
in_str = None

selectors_found = []

depth = 0
media_stack = []

while i < n:
    ch = clean[i]
    if in_str:
        if ch == in_str:
            in_str = None
        buf.append(ch)
    elif ch in ('"', "'"):
        in_str = ch
        buf.append(ch)
    elif ch == '{':
        token = "".join(buf).strip()
        buf = []
        if token.startswith('@media') or token.startswith('@supports') or token.startswith('@keyframes'):
            media_stack.append(token)
        else:
            selectors_found.append((token, media_stack.copy()))
        depth += 1
    elif ch == '}':
        buf = []
        depth -= 1
        if media_stack and depth < len(media_stack):
            media_stack.pop()
    else:
        buf.append(ch)
    i += 1

print(f"Total rule selectors found: {len(selectors_found)}")

bad_selectors = []
for sel, context in selectors_found:
    # Check if selector is empty
    if not sel:
        bad_selectors.append(f"Empty selector inside context: {context}")
        continue
    # Check for trailing/leading comma
    parts = sel.split(',')
    for p in parts:
        p_clean = p.strip()
        if not p_clean:
            bad_selectors.append(f"Empty part in selector list: '{sel}'")
        # Check invalid characters in selector
        # e.g. semicolons, braces, quotes not closed
        if ';' in p_clean:
            bad_selectors.append(f"Semicolon in selector: '{p_clean}'")

print(f"Bad selectors: {len(bad_selectors)}")
for b in bad_selectors[:20]:
    print(b)
