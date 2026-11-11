import json

with open(r'C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        step = obj.get('step_index', 0)
        if 9678 <= step <= 9742:
            stype = obj.get('type')
            if stype == 'USER_INPUT':
                print(f"=== STEP {step} USER ===")
                print(obj.get('content'))
            elif stype == 'PLANNER_RESPONSE':
                # print tool calls
                tc = obj.get('tool_calls', [])
                if tc:
                    for t in tc:
                        print(f"Step {step} TOOL: {t.get('name')} {list(t.get('args', {}).keys())}")
                content = obj.get('content')
                if content:
                    print(f"=== STEP {step} ASSISTANT RESPONSE ===")
                    print(content[:500])
