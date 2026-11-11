from test_lsp_sections import check_css_snippet
import sys

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')

# Find all rule boundary line numbers (lines where brace_depth == 0 and previous line was '}')
boundaries = [0]
brace_depth = 0
in_comment = False
for i, l in enumerate(lines):
    # simple brace tracker
    j = 0
    while j < len(l):
        if not in_comment and j + 1 < len(l) and l[j:j+2] == '/*':
            in_comment = True
            j += 2
            continue
        if in_comment and j + 1 < len(l) and l[j:j+2] == '*/':
            in_comment = False
            j += 2
            continue
        if not in_comment:
            if l[j] == '{':
                brace_depth += 1
            elif l[j] == '}':
                brace_depth -= 1
        j += 1
    if brace_depth == 0 and i > boundaries[-1] + 2000:
        boundaries.append(i + 1)

if boundaries[-1] < len(lines):
    boundaries.append(len(lines))

print(f"Testing in {len(boundaries)-1} chunks...")

total_diags = 0
for k in range(len(boundaries) - 1):
    start = boundaries[k]
    end = boundaries[k+1]
    chunk = "\n".join(lines[start:end])
    diags = check_css_snippet(chunk, f"chunk_{k}")
    if diags:
        print(f"\n--- Chunk lines {start+1}-{end} has {len(diags)} diagnostics: ---")
        for d in diags:
            line_in_chunk = d.get('range', {}).get('start', {}).get('line', 0)
            actual_line = start + line_in_chunk + 1
            print(f"Line {actual_line}: [{d.get('code')}] {d.get('message')}")
        total_diags += len(diags)

print(f"\nScan complete. Total diagnostics across entire style.css: {total_diags}")
