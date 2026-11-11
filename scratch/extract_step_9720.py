import json

with open(r'C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        if obj.get('step_index') == 9720:
            for tc in obj.get('tool_calls', []):
                args = tc.get('args', {})
                print("--- TARGET ---")
                print(args.get('Target'))
                print("--- REPLACEMENT ---")
                print(args.get('Replacement'))
