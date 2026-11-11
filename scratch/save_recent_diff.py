import subprocess

diff = subprocess.check_output(['git', 'diff', '9360d26~1..HEAD', '--', 'static/css/style.css'], text=True, encoding='utf-8')
with open('scratch/recent_diff.txt', 'w', encoding='utf-8') as f:
    f.write(diff)

print("Wrote recent_diff.txt, lines:", len(diff.splitlines()))
