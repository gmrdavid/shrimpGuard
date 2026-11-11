with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

in_comment = False
in_str = None
paren_depth = 0
bracket_depth = 0
brace_depth = 0
errors = []

lines = text.split('\n')
for line_no, line in enumerate(lines, 1):
    i = 0
    while i < len(line):
        ch = line[i]
        nxt = line[i+1] if i+1 < len(line) else ''
        if not in_comment and in_str is None:
            if ch == '/' and nxt == '*':
                in_comment = True
                i += 2
                continue
            elif ch in ('"', "'"):
                in_str = ch
            elif ch == '(':
                paren_depth += 1
            elif ch == ')':
                paren_depth -= 1
                if paren_depth < 0:
                    errors.append(f'Line {line_no}: Unmatched ) in {line}')
                    paren_depth = 0
            elif ch == '[':
                bracket_depth += 1
            elif ch == ']':
                bracket_depth -= 1
                if bracket_depth < 0:
                    errors.append(f'Line {line_no}: Unmatched ] in {line}')
                    bracket_depth = 0
            elif ch == '{':
                brace_depth += 1
            elif ch == '}':
                brace_depth -= 1
                if brace_depth < 0:
                    errors.append(f'Line {line_no}: Unmatched }} in {line}')
                    brace_depth = 0
        elif in_comment:
            if ch == '*' and nxt == '/':
                in_comment = False
                i += 2
                continue
        elif in_str is not None:
            if ch == '\\':
                i += 2
                continue
            elif ch == in_str:
                in_str = None
        i += 1

print('Errors count:', len(errors))
for e in errors[:20]:
    print(e)
print(f'Final paren: {paren_depth}, bracket: {bracket_depth}, brace: {brace_depth}, in_comment: {in_comment}, in_str: {in_str}')
