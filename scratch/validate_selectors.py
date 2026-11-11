with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css_text = f.read()

import re

# Find everything before each top-level or nested '{'
# Let's extract all selectors/at-rules outside declarations
in_comment = False
in_str = None
tokens = []
current = []

for idx, ch in enumerate(css_text):
    if in_comment:
        if ch == '*' and css_text[idx:idx+2] == '*/':
            in_comment = False
    elif in_str:
        if ch == in_str and css_text[idx-1] != '\\':
            in_str = None
    else:
        if ch == '/' and css_text[idx:idx+2] == '/*':
            in_comment = True
        elif ch in ('"', "'"):
            in_str = ch
        elif ch in ('{', '}', ';'):
            piece = "".join(current).strip()
            current = []
            if piece:
                tokens.append((ch, piece, idx))
            continue
    if not in_comment:
        current.append(ch)

print(f"Extracted {len(tokens)} selector/statement chunks.")

# Check chunks preceding '{'
selector_errors = []
for punct, chunk, offset in tokens:
    if punct == '{':
        # This chunk is a selector or @rule!
        # Check if it has suspicious syntax
        # e.g., missing comma, invalid character like <, >, etc.
        # Note: > is valid in child selector! But < or $ or % (unless @keyframes) or ; or : without pseudo
        clean_chunk = re.sub(r'/\*.*?\*/', '', chunk).strip()
        if not clean_chunk:
            selector_errors.append((offset, "Empty selector before {"))
        elif '<' in clean_chunk:
            selector_errors.append((offset, f"Illegal '<' in selector: {clean_chunk}"))
        elif '$' in clean_chunk:
            selector_errors.append((offset, f"Illegal '$' in selector: {clean_chunk}"))

print(f"Selector errors: {len(selector_errors)}")
for off, err in selector_errors:
    print(err)
