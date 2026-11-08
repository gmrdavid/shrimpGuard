content = open("app.py", encoding="utf-8").read().splitlines()
for i, line in enumerate(content, 1):
    if '@app.route("/api/' in line:
        print(f"{i}: {line}")
