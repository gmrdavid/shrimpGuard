import sys
sys.path.insert(0, '.')
from app import app, db, User

with app.app_context():
    users = User.query.all()
    for u in users:
        print(f"User: email='{u.email}', name='{u.user_name}', role='{u.role}', status='{u.status}', hash='{u.password_hash}'")

