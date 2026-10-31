import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
import csv
import zipfile
from app import app, db, User

def run_tests():
    app.config["TESTING"] = True
    client = app.test_client()

    with app.app_context():
        client_user = User.query.filter_by(role="Client").first()
        if not client_user:
            print("FAILED: No Client user found in database.")
            return False

        user_email = client_user.email
        with client.session_transaction() as sess:
            sess["user_id"] = user_email

        # 1. Default Excel export
        r1 = client.get("/historical/export")
        assert r1.status_code == 200, f"Test 1 failed: {r1.status_code}"
        assert "spreadsheetml" in r1.headers.get("Content-Type", "")
        assert "shrimpguard-historical-data.xlsx" in r1.headers.get("Content-Disposition", "")
        print("PASS: Test 1 - Default Excel export OK")

        # 2. Date filtered Excel export
        r2 = client.get("/historical/export?date=2026-10-31&status=all&format=xlsx")
        assert r2.status_code == 200, f"Test 2 failed: {r2.status_code}"
        assert "shrimpguard-historical-2026-10-31-all-statuses.xlsx" in r2.headers.get("Content-Disposition", "")
        print("PASS: Test 2 - Date filtered Excel export OK")

        # 3. Status filtered Excel export
        r3 = client.get("/historical/export?date=all&status=optimal&format=xlsx")
        assert r3.status_code == 200, f"Test 3 failed: {r3.status_code}"
        assert "shrimpguard-historical-all-dates-optimal.xlsx" in r3.headers.get("Content-Disposition", "")
        print("PASS: Test 3 - Status filtered Excel export OK")

        # 4. Filtered CSV export
        r4 = client.get("/historical/export?date=2026-10-31&status=optimal&format=csv")
        assert r4.status_code == 200, f"Test 4 failed: {r4.status_code}"
        assert "text/csv" in r4.headers.get("Content-Type", "")
        assert "shrimpguard-historical-2026-10-31-optimal.csv" in r4.headers.get("Content-Disposition", "")
        reader = csv.reader(io.StringIO(r4.data.decode("utf-8-sig")))
        header = next(reader)
        assert header == ["Date", "Temperature (°C)", "pH", "Status", "WQI Score (%)", "WQI Classification"]
        print("PASS: Test 4 - Filtered CSV export OK")

        # 5. History API returns data
        r5 = client.get("/api/readings/history")
        assert r5.status_code == 200, f"Test 5 failed: {r5.status_code}"
        assert len(r5.json) > 0, "No readings returned from /api/readings/history"
        print(f"PASS: Test 5 - History API returned {len(r5.json)} readings")

    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
    return True

if __name__ == "__main__":
    if not run_tests():
        sys.exit(1)

