import sys
sys.path.insert(0, '.')
from app import app, db, ActivityLog

with app.app_context():
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(20).all()
    print(f"Total logs: {len(logs)}")
    for l in logs:
        print(f"[{l.timestamp}] {l.role} | {l.user_email} | {l.action} | {l.details}")

