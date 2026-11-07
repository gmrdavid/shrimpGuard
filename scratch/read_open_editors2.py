import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\gliam\AppData\Roaming\Code\User\workspaceStorage\89ac34fe414add70d94bd977e4b621b9\state.vscdb')
cur = conn.cursor()
cur.execute('SELECT value FROM ItemTable WHERE key = ?', ('memento/workbench.parts.editor',))
row = cur.fetchone()
if row:
    text = row[0]
    import re
    uris = re.findall(r'\"(?:file|vscode-vfs|untitled):[^\"]+\"', text)
    for u in set(uris):
        print(u)
