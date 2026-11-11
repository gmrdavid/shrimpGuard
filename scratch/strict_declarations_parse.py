import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove comments
def remove_comments(css):
    out = []
    i = 0
    n = len(css)
    in_comment = False
    in_str = None
    while i < n:
        ch = css[i]
        nxt = css[i+1] if i+1 < n else ''
        if in_comment:
            if ch == '*' and nxt == '/':
                in_comment = False
                i += 2
                continue
            i += 1
            continue
        if in_str:
            if ch == '\\':
                out.append(ch)
                out.append(nxt)
                i += 2
                continue
            if ch == in_str:
                in_str = None
            out.append(ch)
            i += 1
            continue
        if ch == '/' and nxt == '*':
            in_comment = True
            i += 2
            continue
        if ch in ('"', "'"):
            in_str = ch
            out.append(ch)
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)

clean_css = remove_comments(text)

# Tokenize rules
# An at-rule or ruleset has `{ ... }`
# Let's extract leaf blocks (blocks that do not contain `{` or `}`)
leaf_blocks = re.findall(r'\{([^{}]+)\}', clean_css)
print(f"Total leaf blocks: {len(leaf_blocks)}")

errors = []
for b_idx, block in enumerate(leaf_blocks):
    # Split by semicolon, but respecting strings and parentheses
    decls = []
    cur = []
    in_str = None
    paren = 0
    for ch in block:
        if in_str:
            if ch == in_str:
                in_str = None
            cur.append(ch)
        elif ch in ('"', "'"):
            in_str = ch
            cur.append(ch)
        elif ch == '(':
            paren += 1
            cur.append(ch)
        elif ch == ')':
            paren -= 1
            cur.append(ch)
        elif ch == ';' and paren == 0:
            decls.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        decls.append("".join(cur).strip())

    for d in decls:
        if not d:
            continue
        # If inside keyframe percentage (e.g. '0%', '100%', 'from', 'to') - wait, leaf block is the declarations INSIDE from { ... }
        if ':' not in d:
            errors.append(f"Leaf block {b_idx}: Declaration missing colon: '{d}'")
        else:
            parts = d.split(':', 1)
            prop = parts[0].strip()
            val = parts[1].strip()
            # check prop
            if not prop:
                errors.append(f"Leaf block {b_idx}: Empty property name before colon: '{d}'")
            elif any(c in prop for c in [' ', '\t', '\n', '\r', '{', '}', ';', '(', ')']):
                errors.append(f"Leaf block {b_idx}: Invalid property name '{prop}'")
            # check val
            if not val:
                errors.append(f"Leaf block {b_idx}: Empty value for property '{prop}'")

print(f"Strict declaration errors: {len(errors)}")
for e in errors[:20]:
    print(e)
