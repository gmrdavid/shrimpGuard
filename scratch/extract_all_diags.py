import os
import glob
import json
import re

logs = glob.glob(r'C:\Users\gliam\AppData\Roaming\Code\logs\20261107T081143\**\*', recursive=True)

all_diags = []

for log in logs:
    if os.path.isfile(log):
        try:
            with open(log, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # look for jsonrpc textDocument/publishDiagnostics
                for m in re.finditer(r'publishDiagnostics.*?\{.*?\}', content, re.DOTALL):
                    all_diags.append((log, m.group(0)[:300]))
                # look for "diagnostics" in general
                for m in re.finditer(r'"diagnostics"\s*:\s*\[(.*?)\]', content, re.DOTALL):
                    d = m.group(1).strip()
                    if d:
                        all_diags.append((log, d))
        except Exception:
            pass

print(f"Total diagnostic matches found: {len(all_diags)}")
for l, d in all_diags[-30:]:
    print("LOG:", os.path.basename(l))
    print("DATA:", d[:250])
    print("="*40)
