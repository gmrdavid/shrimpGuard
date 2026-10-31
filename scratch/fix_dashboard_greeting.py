with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    c = f.read()

target = """<h1 id="dashboard-greeting" data-user-name="{{ user.name if user and user.name else (user.user_name if user and user.user_name else 'Admin') }}">{{ greeting or 'Good day' }}, {{ user.name if user and user.name else (user.user_name if user and user.user_name else 'Admin') }}!</h1>"""

replacement = """<h1 id="dashboard-greeting" data-user-name="{{ user.name if user and user.name else (user.user_name if user and user.user_name else (current_user.name if current_user and current_user.name else 'Rio')) }}">{{ greeting or 'Good day' }}, {{ user.name if user and user.name else (user.user_name if user and user.user_name else (current_user.name if current_user and current_user.name else 'Rio')) }}!</h1>"""

if target in c:
    c = c.replace(target, replacement)
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Updated dashboard.html greeting fallback to Rio")
else:
    print("WARNING: target not found in dashboard.html")

with open('static/js/dashboard.js', 'r', encoding='utf-8') as f:
    js = f.read()

if 'dataset.userName || "Admin"' in js:
    js = js.replace('dataset.userName || "Admin"', 'dataset.userName || "Rio"')
    with open('static/js/dashboard.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Updated dashboard.js fallback to Rio")

