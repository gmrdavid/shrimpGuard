import re

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

# All keyframe names
defined_keyframes = set(re.findall(r'@keyframes\s+([a-zA-Z0-9_-]+)', text))

# All animation properties
# animation: name duration ...
# animation-name: name
anim_names = set()
for match in re.finditer(r'animation(?:-name)?\s*:\s*([^;]+);', text):
    val = match.group(1).strip()
    if val == 'none' or val == 'inherit' or val == 'initial':
        continue
    # Extract the first identifier or words
    words = val.split()
    for w in words:
        w_clean = w.strip(',')
        # ignore timing functions, numbers, iterations
        if re.match(r'^[0-9]', w_clean) or w_clean in ('infinite', 'linear', 'ease', 'ease-in', 'ease-out', 'ease-in-out', 'step-start', 'step-end', 'both', 'forwards', 'backwards', 'normal', 'reverse', 'alternate', 'alternate-reverse', 'running', 'paused', '!important'):
            continue
        if w_clean.startswith('cubic-bezier') or w_clean.startswith('steps'):
            continue
        anim_names.add((w_clean, val))

for name, full in anim_names:
    if name not in defined_keyframes:
        print(f"Unknown keyframe in animation: '{name}' (from '{full}')")
