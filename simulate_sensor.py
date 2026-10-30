import os
import sys
import time
import random
import argparse
import urllib.request
import urllib.parse
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

API_URL = "http://127.0.0.1:5000/api/readings"
SECRET_KEY = os.getenv("SECRET_KEY", "shrimpguard-secret-key-capstone2")


def send_sensor_reading(temperature, ph):
    """
    Sends an automated sensor telemetry reading to the ShrimpGuard API.
    If classified as Warning or Critical, ShrimpGuard automatically pushes
    the alert to ntfy.sh with AI recommendations without any manual button clicking.
    """
    payload = {
        "temperature": round(temperature, 1),
        "ph": round(ph, 2)
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-API-Key": SECRET_KEY
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            status = data.get("status")
            print(f"[OK] Sensor Data Sent -> Temp: {payload['temperature']} °C, pH: {payload['ph']} | ML Status: {status}")
            if status in ("Critical", "Warning"):
                print(f"     >> AUTOMATIC PUSH ALERT DISPATCHED TO NTFY.SH! (Status: {status}) <<")
            else:
                print(f"     (Pond condition is Optimal; no emergency alert needed.)")
            return data
    except urllib.error.URLError as e:
        print(f"[ERROR] Could not connect to ShrimpGuard at {API_URL}.")
        print("        Make sure the web server is running ('python app.py').")
        return None
    except Exception as e:
        print(f"[ERROR] Sensor dispatch failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="ShrimpGuard Automated IoT Sensor Simulator")
    parser.add_argument("--temp", type=float, default=None, help="Custom temperature value in °C")
    parser.add_argument("--ph", type=float, default=None, help="Custom pH level")
    parser.add_argument("--loop", action="store_true", help="Run continuous automated sensor loop")
    parser.add_argument("--interval", type=int, default=30, help="Interval in seconds for continuous loop (default: 30)")
    parser.add_argument("--alert-type", choices=["critical", "warning", "optimal"], default="critical",
                        help="Type of automated reading to simulate (default: critical)")
    args = parser.parse_args()

    print("=====================================================")
    print("  ShrimpGuard Automated Sensor Telemetry Simulator   ")
    print("=====================================================")
    print(f"Target Endpoint: {API_URL}")
    print("No manual button clicking required — alerts dispatch automatically.\n")

    if args.loop:
        print(f"Starting continuous telemetry stream every {args.interval}s. Press Ctrl+C to stop.\n")
        try:
            while True:
                # Generate realistic fluctuating pond readings
                scenario = random.choices(["optimal", "warning", "critical"], weights=[0.6, 0.25, 0.15])[0]
                if scenario == "critical":
                    t = random.choice([round(random.uniform(22.0, 24.5), 1), round(random.uniform(34.2, 36.0), 1)])
                    p = random.choice([round(random.uniform(5.8, 6.4), 2), round(random.uniform(9.1, 9.5), 2)])
                elif scenario == "warning":
                    t = random.choice([round(random.uniform(25.5, 27.5), 1), round(random.uniform(32.2, 33.8), 1)])
                    p = random.choice([round(random.uniform(6.8, 7.4), 2), round(random.uniform(8.6, 8.9), 2)])
                else:
                    t = round(random.uniform(28.5, 31.5), 1)
                    p = round(random.uniform(7.7, 8.3), 2)

                send_sensor_reading(t, p)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nSensor telemetry stream stopped.")
    else:
        # Single reading mode
        if args.temp is not None and args.ph is not None:
            t = args.temp
            p = args.ph
        elif args.alert_type == "critical":
            t = 34.5  # Hyperthermic stress
            p = 9.20  # Toxic alkaline / unionized ammonia hazard
        elif args.alert_type == "warning":
            t = 33.2
            p = 8.75
        else:
            t = 29.5
            p = 8.00

        print(f"Simulating reading for {args.alert_type.upper()} condition...")
        send_sensor_reading(t, p)


if __name__ == "__main__":
    main()

