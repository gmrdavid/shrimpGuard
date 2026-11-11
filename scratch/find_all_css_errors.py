import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# 1. Check for calc() operator spacing errors
print("\n--- Checking calc() syntax ---")
for i, line in enumerate(lines, 1):
    calcs = re.findall(r'calc\([^)]+\)', line)
    for c in calcs:
        # Check for + or - without space around them
        # (Be careful with negative numbers at start of calc or after ( or ,)
        # In CSS calc, + and - must have spaces on BOTH sides.
        # e.g. 100%-20px or 100% -20px or 100%- 20px
        bad_sub = re.search(r'([a-zA-Z0-9%])(-|\+)([a-zA-Z0-9%])', c)
        if bad_sub:
            print(f"Line {i}: Bad spacing in calc: '{c}' (matched '{bad_sub.group(0)}')")
        bad_space_left = re.search(r'([a-zA-Z0-9%])\s+(-|\+)([a-zA-Z0-9%])', c)
        if bad_space_left:
            print(f"Line {i}: Missing space after operator in calc: '{c}' (matched '{bad_space_left.group(0)}')")
        bad_space_right = re.search(r'([a-zA-Z0-9%])(-|\+)\s+([a-zA-Z0-9%])', c)
        if bad_space_right:
            print(f"Line {i}: Missing space before operator in calc: '{c}' (matched '{bad_space_right.group(0)}')")

# 2. Check for invalid hex colors
print("\n--- Checking hex colors ---")
for i, line in enumerate(lines, 1):
    # Find all hex colors
    # Matches # followed by word chars
    hexes = re.findall(r'#[0-9a-fA-F]+', line)
    for h in hexes:
        # hex length without #
        l = len(h) - 1
        if l not in (3, 4, 6, 8):
            # Check if it's an ID selector or inside a comment or hex color
            # If in declaration:
            if ':' in line and line.find(':') < line.find(h):
                print(f"Line {i}: Invalid hex color '{h}' (length {l}): {line.strip()}")

# 3. Check for double semicolons or misplaced colons
print("\n--- Checking semicolons & colons ---")
for i, line in enumerate(lines, 1):
    s = line.strip()
    if ';;' in s and not s.startswith('/*'):
        print(f"Line {i}: Double semicolon: {s}")
    if re.search(r':\s*:', s) and not any(p in s for p in ['::before', '::after', '::backdrop', '::-webkit', '::-moz', '::selection', '::placeholder', '::marker']):
        print(f"Line {i}: Suspicious double colon: {s}")

# 4. Check for nested rules where not supported or braces inside values
print("\n--- Checking braces and at-rules ---")
in_keyframes = False
for i, line in enumerate(lines, 1):
    s = line.strip()
    if '@keyframes' in s:
        in_keyframes = True
    if '@' in s and not s.startswith('/*'):
        # Check at-rules
        valid_ats = ['@media', '@keyframes', '@-webkit-keyframes', '@import', '@font-face', '@supports', '@container', '@layer', '@charset', '@property']
        if not any(s.startswith(at) or f' {at}' in s for at in valid_ats):
            print(f"Line {i}: Suspicious at-rule: {s}")

# 5. Check selectors for invalid trailing/leading commas or empty selectors
print("\n--- Checking selectors ---")
for i, line in enumerate(lines, 1):
    s = line.strip()
    if s.endswith(',') and '{' in s:
        print(f"Line {i}: Selector ending with comma before brace: {s}")
    if s.startswith(',') and not s.startswith('/*'):
        print(f"Line {i}: Selector starting with comma: {s}")
    if ',,' in s and not s.startswith('/*'):
        print(f"Line {i}: Double comma in line: {s}")

# 6. Check for unknown or misspelled CSS properties
print("\n--- Checking properties in declarations ---")
with open('static/css/style.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Strip comments
content_clean = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

# Find all declarations
# Match inside { ... }
decls = re.findall(r'\{([^{}]+)\}', content_clean)
prop_pattern = re.compile(r'^\s*([a-zA-Z\-]+)\s*:\s*(.+)$')
bad_props = set()
for b in decls:
    for item in b.split(';'):
        item = item.strip()
        if not item:
            continue
        m = prop_pattern.match(item)
        if not m:
            # Check if this item is invalid
            if not item.startswith('@'):
                print(f"Unmatched declaration: '{item}'")
        else:
            prop = m.group(1).lower()
            val = m.group(2).strip()
            if prop.startswith('--'):
                continue
            # Check if property has leading dash not in webkit/moz
            if prop.startswith('-') and not (prop.startswith('-webkit-') or prop.startswith('-moz-') or prop.startswith('-ms-') or prop.startswith('-o-')):
                bad_props.add(prop)

if bad_props:
    print("Bad properties found:", bad_props)
else:
    print("All property names follow standard naming conventions.")
