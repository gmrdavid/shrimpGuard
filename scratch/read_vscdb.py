import sqlite3

db_path = r"C:\Users\gliam\AppData\Roaming\Code\User\workspaceStorage\89ac34fe414add70d94bd977e4b621b9\state.vscdb"

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT key, value FROM ItemTable")
rows = c.fetchall()

print(f"Total keys in state.vscdb: {len(rows)}")
for k, v in rows:
    val_str = str(v)
    if 'style.css' in val_str or 'markers' in k.lower() or 'problem' in k.lower() or 'error' in val_str.lower():
        print(f"KEY: {k} (len {len(val_str)})")
        if len(val_str) < 500:
            print(f"VAL: {val_str}")
        else:
            # print snippet around style.css or error
            idx = val_str.find('style.css')
            if idx != -1:
                print(f"SNIPPET style.css: {val_str[max(0, idx-100):min(len(val_str), idx+200)]}")
            idx2 = val_str.find('error')
            if idx2 != -1:
                print(f"SNIPPET error: {val_str[max(0, idx2-100):min(len(val_str), idx2+200)]}")
