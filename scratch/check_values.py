import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

# Strip comments
clean = re.sub(r'/\*.*?\*/', ' ', text, flags=re.DOTALL)

# Find all blocks: { ... }
blocks = re.findall(r'\{([^{}]+)\}', clean)

errors = []
for b in blocks:
    decls = b.split(';')
    for d in decls:
        d = d.strip()
        if not d:
            continue
        if ':' not in d:
            errors.append(f"No colon in declaration: {d}")
            continue
        prop, val = d.split(':', 1)
        prop = prop.strip()
        val = val.strip()

        # Check !important
        if '!' in val:
            if not val.endswith('!important'):
                errors.append(f"Malformed !important: {prop}: {val}")

        # Check parentheses in value
        if val.count('(') != val.count(')'):
            errors.append(f"Unmatched () in value: {prop}: {val}")

        # Check quotes in value
        sq = val.count("'")
        dq = val.count('"')
        if sq % 2 != 0 or dq % 2 != 0:
            errors.append(f"Unmatched quotes in value: {prop}: {val}")

        # Check var()
        if 'var(' in val:
            for vmatch in re.finditer(r'var\(([^)]+)\)', val):
                vcontent = vmatch.group(1).strip()
                vname = vcontent.split(',')[0].strip()
                if not vname.startswith('--'):
                    errors.append(f"Invalid var() variable name '{vname}' in {prop}: {val}")

        # Check rgba() or rgb()
        if 'rgba(' in val or 'rgb(' in val:
            for cmatch in re.finditer(r'rgba?\(([^)]+)\)', val):
                ccontent = cmatch.group(1).strip()
                # If commas: check not trailing comma
                if ccontent.endswith(','):
                    errors.append(f"Trailing comma in rgb/rgba in {prop}: {val}")

print(f"Total value errors: {len(errors)}")
for e in errors[:30]:
    print(e)
