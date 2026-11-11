import json

with open(r'C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        step = obj.get('step_index', 0)
        if 8580 <= step <= 8590:
            print(f"Step {step} ({obj.get('type')} / {obj.get('source')}):")
            content = obj.get('content', '')
            if content:
                print("CONTENT:", content[:300])
            for tc in obj.get('tool_calls', []):
                print("TC:", tc.get('name'), tc.get('args', {}).get('Path'))
