import sys
sys.path.insert(0, '.')
from app import app, db, User

with app.app_context():
    user = User.query.filter_by(email="rio@gmail.com").first()
    print("User found:", user)
    if user:
        print("User name:", user.user_name)
        print("Status:", user.status)
        print("Role:", user.role)
        print("Password check 'rio':", user.check_password("rio"))
        print("Password check 'Rio':", user.check_password("Rio"))

