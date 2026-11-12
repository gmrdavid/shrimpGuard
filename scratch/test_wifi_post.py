import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db, UserDevice, sensor_readings
from sqlalchemy import select

with app.test_client() as client:
    # Send test packet as if coming from Node 2 over Wi-Fi
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "shrimpguard-secret-key-capstone2"
    }
    payload = {
        "temperature": 29.50,
        "ph": 7.95,
        "device_id": "NODE01",
        "seq": 999
    }
    response = client.post("/api/readings", json=payload, headers=headers)
    print("Response status:", response.status_code)
    print("Response json:", response.get_json())

# Check if row was inserted
with app.app_context():
    latest = db.session.execute(
        select(sensor_readings).order_by(sensor_readings.c.id.desc()).limit(1)
    ).mappings().first()
    print("Latest row in DB:", dict(latest) if latest else None)
    
    # Check UserDevice last_seen
    dev = db.session.query(UserDevice).filter_by(device_id="NODE01").first()
    print("UserDevice last_seen:", dev.last_seen if dev else None)
