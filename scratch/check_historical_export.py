with open('static/js/historical.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'table-export-button' in l or 'export' in l.lower():
        print(f"{i+1}: {l.rstrip()}")

