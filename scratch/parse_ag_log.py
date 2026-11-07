import json

with open(r'C:\Users\gliam\AppData\Roaming\Code\logs\20261107T081143\window1\exthost\output_logging_20261107T094604\2-Antigravity LS.log', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for line in lines[-100:]:
    if 'EditorStateMessage' in line or 'ACTIVE_EDITOR_CHANGED' in line or 'diagnostics' in line:
        try:
            # find JSON starting after "=> "
            idx = line.find('=> ')
            if idx != -1:
                obj = json.loads(line[idx+3:].strip())
                print(json.dumps(obj, indent=2)[:500])
                print('='*50)
        except Exception as e:
            print("Error parsing:", e)
