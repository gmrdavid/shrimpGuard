import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\gliam\AppData\Roaming\Code\User\workspaceStorage\89ac34fe414add70d94bd977e4b621b9\state.vscdb')
cur = conn.cursor()
cur.execute('SELECT key, length(value) FROM ItemTable')
rows = cur.fetchall()
for k, l in sorted(rows, key=lambda x: -x[1]):
    print(f"{k}: {l} bytes")
