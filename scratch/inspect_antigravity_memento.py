import sqlite3

db_path = r"C:\Users\gliam\AppData\Roaming\Code\User\workspaceStorage\89ac34fe414add70d94bd977e4b621b9\state.vscdb"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT value FROM ItemTable WHERE key = 'google.google-antigravity'")
row = c.fetchone()
if row:
    text = row[0]
    print(f"Length of google.google-antigravity: {len(text)}")
    # Find occurrences of 'style.css'
    import re
    matches = [m.start() for m in re.finditer(r'style\.css', text)]
    print(f"Occurrences of style.css: {len(matches)}")
    # Show context of the last 3 occurrences
    for m in matches[-5:]:
        start = max(0, m - 150)
        end = min(len(text), m + 200)
        print("--- OCCURRENCE ---")
        print(text[start:end])
