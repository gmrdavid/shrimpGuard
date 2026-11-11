import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's track line and column
line_num = 1
col_num = 1

errors = []
warnings = []

# State machine:
# States:
# TOP_LEVEL (expecting selector or @rule)
# IN_SELECTOR
# IN_AT_RULE
# IN_DECLARATION_BLOCK
# IN_PROPERTY
# IN_VALUE
# IN_COMMENT
# IN_STRING

i = 0
n = len(text)
brace_stack = [] # stores (brace_char, line, col, context)

in_comment = False
comment_start = (0, 0)

in_str = None
str_start = (0, 0)

current_token = []
selector_buffer = []
block_depth = 0

while i < n:
    ch = text[i]
    line = line_num
    col = col_num
    
    # Update line & col for next char
    if ch == '\n':
        line_num += 1
        col_num = 1
    else:
        col_num += 1

    # Comment handling
    if in_comment:
        if ch == '*' and i + 1 < n and text[i+1] == '/':
            in_comment = False
            i += 2
            col_num += 1
            continue
        i += 1
        continue
    
    if ch == '/' and i + 1 < n and text[i+1] == '*':
        in_comment = True
        comment_start = (line, col)
        i += 2
        col_num += 1
        continue

    # String handling
    if in_str:
        if ch == '\\':
            # Skip escaped char
            i += 2
            col_num += 1
            continue
        elif ch == in_str:
            in_str = None
        i += 1
        continue
    
    if ch in ('"', "'"):
        in_str = ch
        str_start = (line, col)
        i += 1
        continue

    # Braces
    if ch == '{':
        brace_stack.append((ch, line, col, "".join(selector_buffer).strip()))
        selector_buffer = []
        i += 1
        continue
    elif ch == '}':
        if not brace_stack:
            errors.append(f"Line {line}:{col}: Unmatched closing brace '}}'")
        else:
            brace_stack.pop()
        selector_buffer = []
        i += 1
        continue

    # If outside block, accumulate selector
    if len(brace_stack) == 0:
        selector_buffer.append(ch)
    else:
        # Inside block: could be nested @media or declarations
        selector_buffer.append(ch)

    i += 1

if in_comment:
    errors.append(f"Unclosed comment starting at line {comment_start[0]}:{comment_start[1]}")
if in_str:
    errors.append(f"Unclosed string starting at line {str_start[0]}:{str_start[1]}")
if brace_stack:
    for b, l, c, ctx in brace_stack:
        errors.append(f"Unclosed brace from line {l}:{c} near '{ctx[-40:]}'")

print(f"Strict parse completed with {len(errors)} structural errors.")
for e in errors:
    print("ERROR:", e)
