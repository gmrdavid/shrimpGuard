with open('scratch/check_declarations.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('for lno, text in suspicious[:50]:', 'for lno, text in suspicious[100:]:').replace('without semicolon (128):', 'last 28:')
with open('scratch/check_declarations_3.py', 'w', encoding='utf-8') as f:
    f.write(code)
