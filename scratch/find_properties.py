import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

# Strip comments
clean = re.sub(r'/\*.*?\*/', ' ', text, flags=re.DOTALL)

# Find all declarations: word: value;
# A declaration is inside { ... }
# Let's find all `{ [^}]+ }`
blocks = re.findall(r'\{([^{}]+)\}', clean)

props = set()
decl_lines = []

for b in blocks:
    parts = b.split(';')
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if ':' in p:
            prop_name = p.split(':', 1)[0].strip()
            # If it doesn't contain spaces or newlines:
            if '\n' in prop_name or ' ' in prop_name:
                decl_lines.append((prop_name, p))
            else:
                props.add(prop_name)
        else:
            decl_lines.append(('NO_COLON', p))

print(f"Total distinct properties: {len(props)}")
print(f"Suspicious declarations with spaces/newlines in prop name: {len(decl_lines)}")
for pl, full in decl_lines[:30]:
    print(f"PROP: [{pl}] FULL: [{full[:80]}]")
