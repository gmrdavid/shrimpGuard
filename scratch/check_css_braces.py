with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

# Check balanced braces in style.css
opens = 0
closes = 0
errors = []
line = 1
col = 1
for idx, ch in enumerate(text):
    if ch == '\n':
        line += 1
        col = 1
    else:
        col += 1
    if ch == '{':
        opens += 1
    elif ch == '}':
        closes += 1
        if closes > opens:
            errors.append(f"Unmatched closing brace at line {line}, col {col}")

print(f"Total lines: {line}")
print(f"Opens: {opens}, Closes: {closes}")
if errors:
    print("Brace errors:", errors[:10])
