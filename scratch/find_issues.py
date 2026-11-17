with open('templates/devices.html', 'r', encoding='utf-8') as f:
    text = f.read()

count = text.count('style="')
print(f"Total inline style attributes in devices.html: {count}")
