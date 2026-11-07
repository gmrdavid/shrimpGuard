import sqlite3
import json

conn = sqlite3.connect(r'C:\Users\gliam\AppData\Roaming\Code\User\workspaceStorage\89ac34fe414add70d94bd977e4b621b9\state.vscdb')
cur = conn.cursor()
cur.execute('SELECT value FROM ItemTable WHERE key = ?', ('memento/workbench.parts.editor',))
row = cur.fetchone()
if row:
    data = json.loads(row[0])
    # print open editor resources
    def find_uris(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'resource':
                    print('OPEN:', v)
                else:
                    find_uris(v)
        elif isinstance(obj, list):
            for item in obj:
                find_uris(item)
    find_uris(data)
