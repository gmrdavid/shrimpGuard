import sys
sys.path.insert(0, '.')
from app import app, db, User

with app.app_context():
    david = db.session.get(User, 'david@gmail.com')
    rio = db.session.get(User, 'rio@gmail.com')
    print("Checking David password:")
    for p in ['admin', 'david', 'David', '123456', '12345678', 'password', 'admin123', 'David123', 'ShrimpGuard']:
        if david.check_password(p):
            print("DAVID'S PASSWORD IS:", p)
            break

