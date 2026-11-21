with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

import re
pos = css.find('.notif-topic')
if pos != -1:
    print("=== NOTIF TOPIC CSS ===")
    print(css[pos-100:pos+1500])
else:
    print(".notif-topic not found")
