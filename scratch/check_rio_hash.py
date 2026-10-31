import sys
sys.path.insert(0, '.')
from app import app, db, User

with app.app_context():
    user = User.query.filter_by(email="rio@gmail.com").first()
    print("Email:", user.email)
    print("User name:", user.user_name)
    print("Password hash:", user.password_hash)
    test_pwds = ["rio123", "Rio123", "rio1234", "password", "12345678", "Rio@123", "Rio123!", "rio@gmail.com", "Rio", "rio", "NewSecretPassword123!"]
    for p in test_pwds:
        if user.check_password(p):
            print(f"MATCH FOUND! Password is: '{p}'")
            break
    else:
        print("None of test passwords matched.")
