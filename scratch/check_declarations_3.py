import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_comment = False
in_rule = False
brace_depth = 0
suspicious = []

for line_no, raw_line in enumerate(lines, 1):
    line = raw_line.strip()
    
    # Handle comments
    # remove single-line block comments /* ... */
    clean_line = re.sub(r'/\*.*?\*/', '', line).strip()
    
    if '/*' in clean_line:
        in_comment = True
        clean_line = clean_line[:clean_line.index('/*')].strip()
    elif '*/' in clean_line:
        in_comment = False
        clean_line = clean_line[clean_line.index('*/')+2:].strip()
    elif in_comment:
        continue

    if not clean_line:
        continue

    # Count braces
    brace_depth += clean_line.count('{') - clean_line.count('}')

    # If inside a rule block (and not an @keyframes or @media line itself)
    if brace_depth > 0:
        # Check if line looks like a declaration but missing semicolon or malformed
        # Ignored if ends with { or } or is an at-rule or selector
        if not clean_line.endswith('{') and not clean_line.endswith('}') and not clean_line.endswith(';'):
            # It might be a multiline property or broken line
            suspicious.append((line_no, clean_line))

print(f'Suspicious lines without semicolon ({len(suspicious)}):')
for lno, text in suspicious[100:]:
    print(f'Line {lno}: {text}')
