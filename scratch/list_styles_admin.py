import re

for filename in ['templates/admin_telemetry.html', 'templates/dashboard.html']:
    print(f"=== {filename} ===")
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'style="([^"]*)"', line):
            val = m.group(1)
            if '{' in val or '}' in val or '%' in val:
                print(f"Line {i}: {val}")
