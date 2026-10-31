from werkzeug.security import check_password_hash

orig_hash = "scrypt:32768:8:1$6u4W2X4ZILkR9ZqD$204a0c20041a083f08f04f2234223dab07ccca803cd60b3ecfdb4f5b64f2539b07e0ac138636aa3abeddce63956cd1fc4c1fe9558a30f4e63206cb4bfe96c19d"

candidates = [
    "rio", "Rio", "RioD", "riod", "rio123", "Rio123", "Rio123!", "rio@123", "rio2026",
    "password", "Password", "Password123", "Password123!", "12345678", "123456", "1234",
    "admin", "client", "shrimpguard", "ShrimpGuard", "shrimp", "Shrimp", "user", "User",
    "capstone", "Capstone", "capstone2", "Capstone2", "rio@gmail.com", "david@gmail.com",
    "david", "David", "test", "Test1234"
]

print("Checking candidates against original hash...")
for c in candidates:
    if check_password_hash(orig_hash, c):
        print(f"FOUND MATCH! Password is: '{c}'")
        break
else:
    print("None matched in basic candidates.")

