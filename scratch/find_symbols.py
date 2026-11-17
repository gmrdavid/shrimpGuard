import os

for root, dirs, files in os.walk('templates'):
    for f in files:
        if f.endswith('.html'):
            p = os.path.join(root, f)
            c = open(p, encoding='utf-8', errors='ignore').read()
            if '<symbol' in c or 'icon-eye' in c:
                print('Found in:', p)
