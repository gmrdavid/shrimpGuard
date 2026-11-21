with open('static/css/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('users-icon')
if pos != -1:
    print("users-icon:", text[pos-100:pos+500])

pos2 = text.find('system-icon')
if pos2 != -1:
    print("system-icon:", text[pos2-100:pos2+500])
