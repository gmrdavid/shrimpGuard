import re

with open(r'C:\Users\gliam\AppData\Roaming\Code\logs\20261107T081143\window1\exthost\output_logging_20261107T094604\7-Gemini Code Assist.log', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

pos = 0
found = []
while True:
    idx = text.find('"diagnostics":[', pos)
    if idx == -1:
        break
    end_idx = text.find(']', idx)
    if end_idx != -1:
        diag_str = text[idx+14:end_idx+1]
        if diag_str != '[]':
            uri_idx = text.find('"uri":', end_idx)
            uri_str = text[uri_idx:uri_idx+150] if uri_idx != -1 else ''
            found.append((diag_str, uri_str))
    pos = idx + 1

for d, u in found[-20:]:
    print('DIAG:', d)
    print('URI :', u)
    print('-'*40)
