with open('scratch/check_declarations.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Modify to print all
code = code.replace('for lno, text in suspicious[:50]:', 'for lno, text in suspicious[50:]:').replace('without semicolon (128):', 'remaining:')
with open('scratch/check_declarations_2.py', 'w', encoding='utf-8') as f:
    f.write(code)
