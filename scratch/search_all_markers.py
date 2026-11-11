import sqlite3
import json

db_path = r"C:\Users\gliam\AppData\Roaming\Code\User\workspaceStorage\89ac34fe414add70d94bd977e4b621b9\state.vscdb"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT key, value FROM ItemTable")
rows = c.fetchall()

found = 0
for k, v in rows:
    v_str = str(v)
    if any(w in v_str.lower() for w in ['style.css', 'diagnostic', 'marker', 'problem', 'syntaxerror', 'css(']):
        print(f"Key: {k}")
        # print if reasonable length
        if len(v_str) < 300:
            print(f"  Value: {v_str}")
        found += 1

print(f"Total matching keys: {found}")
