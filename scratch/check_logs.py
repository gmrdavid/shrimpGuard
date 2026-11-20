import pymysql
import os
from dotenv import load_dotenv

load_dotenv()
conn = pymysql.connect(
    host=os.getenv('DB_HOST', '127.0.0.1'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD') or '',
    db=os.getenv('DB_NAME', 'aeris_v')
)
cur = conn.cursor()
cur.execute("SELECT timestamp, action, user_email, user_name, details FROM activity_logs WHERE action IN ('SIGNUP', 'USER_CREATE', 'PASSWORD_RESET', 'LOGIN') ORDER BY timestamp DESC LIMIT 20")
for r in cur.fetchall():
    print(r)
