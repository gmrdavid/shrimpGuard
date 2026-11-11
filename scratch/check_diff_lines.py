import subprocess
import re

res = subprocess.run(['git', 'diff', '09e8077', 'HEAD', 'static/css/style.css'], capture_output=True, text=True, encoding='utf-8')
diff_text = res.stdout

added_lines = []
for line in diff_text.split('\n'):
    if line.startswith('+') and not line.startswith('+++'):
        added_lines.append(line[1:])

print(f"Total added lines: {len(added_lines)}")

# Let's inspect the added lines for any syntax errors or strange constructs
for idx, l in enumerate(added_lines, 1):
    s = l.strip()
    # Check for suspicious things in added lines
    if not s or s.startswith('/*') or s.startswith('*') or s.endswith('*/'):
        continue
    # check unclosed or mismatched quotes
    sq = s.count("'")
    dq = s.count('"')
    if sq % 2 != 0:
        print(f"Added line {idx}: Unmatched ' in: {s}")
    if dq % 2 != 0:
        print(f"Added line {idx}: Unmatched \" in: {s}")
    # check bad semicolons
    if s.endswith(';;'):
        print(f"Added line {idx}: Double semicolon in: {s}")
    # check property without colon
    if s.endswith(';') and ':' not in s:
        print(f"Added line {idx}: Missing colon in: {s}")
