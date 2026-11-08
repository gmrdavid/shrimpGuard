import os
import re

for root, dirs, files in os.walk('templates'):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            with open(p, encoding='utf-8') as fh:
                text = fh.read()
            matches = re.findall(r'name=["\']csrf_token["\'][^>]*>', text)
            if matches:
                print(f, matches)
