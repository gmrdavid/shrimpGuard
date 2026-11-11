import subprocess

diff = subprocess.check_output(['git', 'diff', 'baf3a61~1', 'baf3a61', '--', 'static/css/style.css'], text=True, encoding='utf-8')
print(f"Diff size: {len(diff.splitlines())} lines")

added_lines = []
for line in diff.splitlines():
    if line.startswith('+') and not line.startswith('+++'):
        added_lines.append(line[1:])

print(f"Total added lines: {len(added_lines)}")
for i, l in enumerate(added_lines):
    s = l.strip()
    if s and not s.startswith('/*') and not s.endswith('*/') and not s.endswith('{') and not s.endswith('}') and not s.endswith(';') and not s.endswith(','):
        print(f"Suspicious line: [{s}]")
