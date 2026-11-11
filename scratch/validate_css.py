import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css_text = f.read()

# Let's map character offset to line and column
line_starts = [0]
for idx, ch in enumerate(css_text):
    if ch == '\n':
        line_starts.append(idx + 1)

def offset_to_loc(offset):
    import bisect
    line_no = bisect.bisect_right(line_starts, offset)
    col_no = offset - line_starts[line_no - 1] + 1
    return line_no, col_no

errors = []

# Strip comments while preserving character positions (replace with spaces)
clean_chars = list(css_text)
i = 0
n = len(css_text)

while i < n:
    if i + 1 < n and css_text[i] == '/' and css_text[i+1] == '*':
        start = i
        i += 2
        while i + 1 < n and not (css_text[i] == '*' and css_text[i+1] == '/'):
            i += 1
        i += 2 # skip */
        for j in range(start, min(i, n)):
            if clean_chars[j] != '\n':
                clean_chars[j] = ' '
    else:
        i += 1

cleaned = "".join(clean_chars)

# Now let's parse top-level constructs: selectors, @rules, and blocks
pos = 0
def skip_ws(p):
    while p < n and cleaned[p] in ' \t\r\n':
        p += 1
    return p

# Let's check for any declaration inside { ... }
# We can find each block { ... } and check its contents
stack = []
block_ranges = [] # (start_content, end_content, is_keyframes)

i = 0
in_str = None
while i < n:
    ch = cleaned[i]
    if in_str:
        if ch == '\\':
            i += 2
            continue
        elif ch == in_str:
            in_str = None
    else:
        if ch in ('"', "'"):
            in_str = ch
        elif ch == '{':
            # look behind for @keyframes
            before = cleaned[max(0, i-50):i]
            is_kf = '@keyframes' in before
            stack.append((i, is_kf))
        elif ch == '}':
            if stack:
                start_idx, is_kf = stack.pop()
                block_ranges.append((start_idx + 1, i, is_kf, len(stack)))
            else:
                l, c = offset_to_loc(i)
                errors.append(f"Line {l}:{c} Unexpected closing brace '}}'")
    i += 1

if stack:
    for s_idx, _ in stack:
        l, c = offset_to_loc(s_idx)
        errors.append(f"Line {l}:{c} Unclosed brace '{{'")

# Now for each innermost block (where declaration statements live)
# A block is innermost if it doesn't contain other blocks, OR if it's not a media query wrapper
# Actually, declarations are separated by ';'
# Let's validate declarations in leaf blocks!

leaf_blocks = []
for start, end, is_kf, depth in block_ranges:
    # Check if this block contains another '{'
    inner_has_block = '{' in cleaned[start:end]
    if not inner_has_block:
        leaf_blocks.append((start, end, is_kf))

print(f"Total leaf blocks to validate: {len(leaf_blocks)}")

for start, end, is_kf in leaf_blocks:
    content = cleaned[start:end]
    # Split content by ';' while respecting strings and parentheses ()
    decls = []
    curr = []
    p_depth = 0
    b_depth = 0
    s_in = None
    char_offset = start
    decl_start_offset = start
    
    idx = 0
    while idx < len(content):
        c = content[idx]
        if s_in:
            if c == '\\':
                curr.append(c)
                idx += 1
                if idx < len(content):
                    curr.append(content[idx])
            elif c == s_in:
                s_in = None
                curr.append(c)
            else:
                curr.append(c)
        else:
            if c in ('"', "'"):
                s_in = c
                curr.append(c)
            elif c == '(':
                p_depth += 1
                curr.append(c)
            elif c == ')':
                p_depth -= 1
                curr.append(c)
            elif c == ';':
                if p_depth == 0:
                    decls.append(("".join(curr), decl_start_offset, start + idx))
                    curr = []
                    decl_start_offset = start + idx + 1
                else:
                    curr.append(c)
            else:
                curr.append(c)
        idx += 1
    
    if curr:
        remainder = "".join(curr).strip()
        if remainder:
            # Trailing declaration without semicolon before '}'
            decls.append((remainder, decl_start_offset, end))

    for d_text, d_start, d_end in decls:
        d = d_text.strip()
        if not d:
            continue
        
        # Check if declaration has a colon
        if ':' not in d:
            l, c = offset_to_loc(d_start)
            # Maybe it's a keyframe selector like 'from' or '0%' or 'to' or '100%' if inside keyframes
            if is_kf and d in ('from', 'to') or re.match(r'^\d+%$', d):
                continue
            errors.append(f"Line {l}:{c} Declaration missing colon: '{d}'")
            continue
        
        prop, val = d.split(':', 1)
        prop = prop.strip()
        val = val.strip()
        
        # Validate property name
        if not re.match(r'^(-?[a-zA-Z_][a-zA-Z0-9_-]*|--[a-zA-Z0-9_-]+)$', prop):
            l, c = offset_to_loc(d_start)
            errors.append(f"Line {l}:{c} Invalid CSS property name: '{prop}' in '{d[:60]}'")
        
        if not val:
            l, c = offset_to_loc(d_start)
            errors.append(f"Line {l}:{c} Property '{prop}' has empty value")

print(f"Validation finished. Total errors: {len(errors)}")
for err in errors[:30]:
    print(err)
