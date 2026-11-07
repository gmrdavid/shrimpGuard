import sqlite3

conn = sqlite3.connect(r'C:\Users\gliam\AppData\Roaming\Code\User\workspaceStorage\89ac34fe414add70d94bd977e4b621b9\state.vscdb')
cur = conn.cursor()
for key in ['memento/workbench.panel.markers', 'codelens/cache2', 'ms-python.python']:
    cur.execute('SELECT value FROM ItemTable WHERE key = ?', (key,))
    row = cur.fetchone()
    print('KEY:', key)
    if row:
        print(row[0])
    print('='*40)
