import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')

issues = []

# 1. Check for bad hex colors (# followed by alphanumeric that isn't 3, 4, 6, or 8 chars)
hex_pattern = re.compile(r'#([0-9a-fA-F]+)\b')
for lno, line in enumerate(lines, 1):
    # skip comments
    if '/*' in line or '*/' in line:
        continue
    for match in hex_pattern.finditer(line):
        h = match.group(1)
        if len(h) not in (3, 4, 6, 8):
            issues.append(f"Line {lno}: Invalid hex color #{h} in: {line.strip()}")

# 2. Check for invalid calc expressions (e.g. calc(100% - 10px) must have spaces around - and +)
# In CSS: calc(100%-10px) is an ERROR! CSS spec requires whitespace around + and - operators in calc()
calc_pattern = re.compile(r'calc\(([^)]+)\)')
for lno, line in enumerate(lines, 1):
    for match in calc_pattern.finditer(line):
        expr = match.group(1)
        # Check if there is + or - not surrounded by spaces or at start (e.g. 100%-10px)
        # But allow negative numbers like -10px
        bad_minus = re.search(r'[0-9a-zA-Z%)]-(?!\s)', expr)
        if bad_minus:
            issues.append(f"Line {lno}: calc() missing whitespace around '-': {line.strip()}")
        bad_plus = re.search(r'[0-9a-zA-Z%)]\+(?!\s)|\S\+[0-9a-zA-Z%]', expr)
        if bad_plus:
            issues.append(f"Line {lno}: calc() missing whitespace around '+': {line.strip()}")

# 3. Check for double semicolons or trailing typos
for lno, line in enumerate(lines, 1):
    if ';;' in line:
        issues.append(f"Line {lno}: Double semicolon: {line.strip()}")

# 4. Check for invalid rgb/rgba: rgba(0, 0, 0, 0.5) vs missing commas or unbalanced
for lno, line in enumerate(lines, 1):
    if 'rgba(' in line or 'rgb(' in line:
        # check unclosed or malformed
        pass

# 5. Check for property lines missing colon
# A line inside a block that has words followed by semicolon but no colon
for lno, line in enumerate(lines, 1):
    s = line.strip()
    if s.endswith(';') and ':' not in s and not s.startswith('/*'):
        issues.append(f"Line {lno}: Declaration missing colon: {s}")

# 6. Check for stray characters between rules (brace_depth == 0)
in_comment = False
brace_depth = 0
for lno, line in enumerate(lines, 1):
    s = line.strip()
    clean = re.sub(r'/\*.*?\*/', '', s).strip()
    if '/*' in clean:
        in_comment = True
        clean = clean[:clean.index('/*')].strip()
    elif '*/' in clean:
        in_comment = False
        clean = clean[clean.index('*/')+2:].strip()
    elif in_comment:
        continue

    if not clean:
        continue

    brace_depth += clean.count('{') - clean.count('}')
    if brace_depth == 0 and not clean.endswith('{') and not clean.endswith('}') and not clean.startswith('@'):
        # Outside any rule, but line doesn't end with { and isn't a selector or comment!
        # Could be an orphan declaration or stray property!
        if ':' in clean and clean.endswith(';'):
            issues.append(f"Line {lno}: Orphan CSS property outside of any selector block: {clean}")

print(f"Total issues found: {len(issues)}")
for iss in issues[:40]:
    print(iss)
