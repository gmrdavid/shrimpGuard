import json

with open(r'C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        step = obj.get('step_index', 0)
        if step in (9716, 9720, 9724):
            print(f"=== STEP {step} ===")
            for tc in obj.get('tool_calls', []):
                print(tc.get('name'))
                args = tc.get('args', {})
                print("PATH:", args.get('Path'))
                print("TARGET:", repr(args.get('Target'))[:200])
                print("REPLACEMENT:", repr(args.get('Replacement'))[:200])
