import subprocess

diff = subprocess.check_output(['git', 'diff', 'c6126b8~1', 'c6126b8', '--', 'static/css/style.css'], text=True, encoding='utf-8')
print(f"Diff size: {len(diff.splitlines())} lines")

# Let's inspect all added lines (+)
added_lines = []
for line in diff.splitlines():
    if line.startswith('+') and not line.startswith('+++'):
        added_lines.append(line[1:])

print(f"Total added lines: {len(added_lines)}")
for i, l in enumerate(added_lines):
    # Check for any suspicious syntax:
    # missing semicolons, unmatched braces, invalid properties, etc.
    s = l.strip()
    if s and not s.startswith('/*') and not s.endswith('*/') and not s.endswith('{') and not s.endswith('}') and not s.endswith(';') and not s.endswith(','):
        print(f"Suspicious line (no ;, comma, or brace): [{s}]")
