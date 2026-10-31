with open('static/js/monitoring.js', 'r', encoding='utf-8') as f:
    text = f.read()

print("monitoring.js length:", len(text))
# Check if there are syntax errors by compiling JS or checking functions
import re
functions = re.findall(r'function\s+([a-zA-Z0-9_]+)', text)
print("Functions in monitoring.js:", functions)

