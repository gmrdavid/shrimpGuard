import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\gliam\AppData\Roaming\Code\User\workspaceStorage\89ac34fe414add70d94bd977e4b621b9\state.vscdb')
c = conn.cursor()
c.execute("SELECT value FROM ItemTable WHERE key = 'memento/workbench.editors.files.textFileEditor'")
row = c.fetchone()
val = json.loads(row[0])
print("Keys:", list(val.keys()))
for k, v in val.items():
    if isinstance(v, list):
        for item in v:
            if 'style.css' in str(item):
                print(f"Key {k} has style.css:")
                print(item)
    elif isinstance(v, dict):
        for subk, subv in v.items():
            if 'style.css' in str(subk) or 'style.css' in str(subv):
                print(f"Key {k} -> {subk} has style.css:")
                print(subv)
