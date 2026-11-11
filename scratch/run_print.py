with open('scratch/find_properties.py', 'r', encoding='utf-8') as f:
    code = f.read()

code += """
print(sorted(list(props)))
"""
with open('scratch/find_properties_print.py', 'w', encoding='utf-8') as f:
    f.write(code)
