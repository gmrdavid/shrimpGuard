import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')

# Check line by line for:
# 1. Unmatched parentheses in a single line (unless multiline)
# 2. Unmatched quotes in a single line (unless multiline)
# 3. Property name with spaces inside (e.g. "border radius:")
# 4. Value with bad tokens
# 5. Invalid characters like backtick ` or unescaped non-ascii or stray HTML

issues = []

for lno, line in enumerate(lines, 1):
    stripped = line.strip()
    # ignore comments
    if stripped.startswith('/*') or stripped.startswith('*') or stripped.endswith('*/'):
        continue
    
    # check for HTML tags like <div or </ or <span or <svg
    if re.search(r'<(div|span|svg|p|button|input|form|use|path|a|h\d)\b', stripped, re.IGNORECASE):
        issues.append((lno, f"HTML tag found in CSS: {stripped}"))

    # check for backticks
    if '`' in stripped:
        issues.append((lno, f"Backtick found in CSS: {stripped}"))

    # check for property name with spaces before colon:
    # e.g. "  foo bar: 10px;" but not selectors like "div span {"
    if ':' in stripped and not stripped.endswith('{') and not stripped.endswith(','):
        # check if it's a declaration line
        parts = stripped.split(':', 1)
        prop = parts[0].strip()
        val = parts[1].strip()
        # if prop has spaces and doesn't look like a selector or pseudo-selector:
        # e.g. "div:hover" is not declaration, but "border color: red" is!
        if ' ' in prop and not any(p in prop for p in ('.', '#', '[', '>', '+', '~', '@')):
            issues.append((lno, f"Property name with spaces: '{prop}' in: {stripped}"))

    # check for unclosed single quote or double quote on a single line declaration
    if ':' in stripped and stripped.endswith(';'):
        # count quotes
        # strip escaped quotes
        no_esc = stripped.replace('\\"', '').replace("\\'", "")
        sq_count = no_esc.count("'")
        dq_count = no_esc.count('"')
        if sq_count % 2 != 0:
            issues.append((lno, f"Unmatched single quote: {stripped}"))
        if dq_count % 2 != 0:
            issues.append((lno, f"Unmatched double quote: {stripped}"))

    # check for unmatched parentheses on lines ending with ;
    if stripped.endswith(';'):
        if stripped.count('(') != stripped.count(')'):
            # check if previous line started it
            issues.append((lno, f"Mismatched parentheses: {stripped}"))

print(f"Total syntax issues found: {len(issues)}")
for lno, msg in issues:
    print(f"Line {lno}: {msg}")
