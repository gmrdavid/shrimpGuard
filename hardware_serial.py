"""
===================================================================================
ShrimpGuard - Built-in Hardware LoRa Serial Listener (Zero-Dependency Win32)
===================================================================================
Directly connects to the Node 2 LoRa Receiver on Windows via standard-library ctypes
without requiring pyserial or any external dependencies.

Features:
  - Auto-detects active COM ports (COM8, COM5, etc.)
  - Listens to incoming LoRa telemetry packets from Node 1 (Pond sensors)
  - Automatically ingests readings into ShrimpGuard database ('sensors' table)
  - Seamlessly updates live dashboard and triggers ntfy emergency alerts
===================================================================================
"""

import ctypes
from ctypes import wintypes
import logging
import os
import re
import threading
import time
from datetime import datetime

logger = logging.getLogger("HardwareSerial")

# Win32 Constants
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = -1

# DCB Structure
class DCB(ctypes.Structure):
    _fields_ = [
        ("DCBlength", wintypes.DWORD),
        ("BaudRate", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("wReserved", wintypes.WORD),
        ("XonLim", wintypes.WORD),
        ("XoffLim", wintypes.WORD),
        ("ByteSize", wintypes.BYTE),
        ("Parity", wintypes.BYTE),
        ("StopBits", wintypes.BYTE),
        ("XonChar", ctypes.c_char),
        ("XoffChar", ctypes.c_char),
        ("ErrorChar", ctypes.c_char),
        ("EofChar", ctypes.c_char),
        ("EvtChar", ctypes.c_char),
        ("wReserved1", wintypes.WORD),
    ]

# COMMTIMEOUTS Structure
class COMMTIMEOUTS(ctypes.Structure):
    _fields_ = [
        ("ReadIntervalTimeout", wintypes.DWORD),
        ("ReadTotalTimeoutMultiplier", wintypes.DWORD),
        ("ReadTotalTimeoutConstant", wintypes.DWORD),
        ("WriteTotalTimeoutMultiplier", wintypes.DWORD),
        ("WriteTotalTimeoutConstant", wintypes.DWORD),
    ]

kernel32 = ctypes.windll.kernel32

# In-memory latest hardware state for instant frontend sync
LATEST_HARDWARE_STREAM = {
    "temperature": None,
    "ph": None,
    "device_id": "NODE01",
    "seq": None,
    "rssi": None,
    "snr": None,
    "status": None,
    "recorded_at": None,
    "connected_port": None,
    "is_connected": False,
    "last_packet_time": 0,
}


def parse_telemetry_line(raw_line):
    """
    Parses incoming telemetry line from Node 2 LoRa receiver.
    Supports:
      1. Diagnostic format: [RX] OK  Node=NODE01 | Seq=2215 | Temp=27.62 C | pH=5.32 | Status=Critical ...
      2. Structured JSON: LORA_JSON:{"device":"NODE01","seq":42,"temperature":28.56,"ph":7.82,...}
      3. Raw CSV format: SG1,NODE01,42,28.56,7.82,Optimal
    """
    if not raw_line:
        return None
    line = raw_line.strip()

    # 1. Diagnostic text output from Node 2
    if "[RX] OK" in line:
        dev_m = re.search(r"Node=([A-Za-z0-9_-]+)", line)
        seq_m = re.search(r"Seq=(\d+)", line)
        temp_m = re.search(r"Temp=([-+]?[0-9]*\.?[0-9]+)", line)
        ph_m = re.search(r"pH=([-+]?[0-9]*\.?[0-9]+)", line)
        stat_m = re.search(r"Status=([A-Za-z]+)", line)
        rssi_m = re.search(r"RSSI=([-+]?[0-9]+)", line)
        snr_m = re.search(r"SNR=([-+]?[0-9]*\.?[0-9]+)", line)

        if temp_m and ph_m:
            try:
                return {
                    "temperature": float(temp_m.group(1)),
                    "ph": float(ph_m.group(1)),
                    "device_id": dev_m.group(1) if dev_m else "NODE01",
                    "seq": int(seq_m.group(1)) if seq_m else None,
                    "status_hint": stat_m.group(1) if stat_m else None,
                    "rssi": float(rssi_m.group(1)) if rssi_m else None,
                    "snr": float(snr_m.group(1)) if snr_m else None,
                }
            except Exception:
                pass

    # 2. Structured JSON format
    if "LORA_JSON:" in line:
        import json
        try:
            part = line.split("LORA_JSON:", 1)[1].strip()
            data = json.loads(part)
            return {
                "temperature": float(data.get("temperature", data.get("temp", 0))),
                "ph": float(data.get("ph", 0)),
                "device_id": data.get("device", "NODE01"),
                "seq": data.get("seq"),
                "status_hint": data.get("status"),
                "rssi": data.get("rssi"),
                "snr": data.get("snr"),
            }
        except Exception:
            pass

    # 3. Raw LoRa CSV format
    if line.startswith("SG1,"):
        parts = line.split(",")
        if len(parts) >= 5:
            try:
                return {
                    "temperature": float(parts[3]),
                    "ph": float(parts[4]),
                    "device_id": parts[1],
                    "seq": int(parts[2]),
                    "status_hint": parts[5] if len(parts) > 5 else None,
                }
            except ValueError:
                pass

    return None


def open_win32_port(port_name, baud_rate=115200):
    """Opens a COM port on Windows using kernel32 CreateFileW."""
    handle = kernel32.CreateFileW(
        f"\\\\.\\{port_name}",
        GENERIC_READ | GENERIC_WRITE,
        0,
        None,
        OPEN_EXISTING,
        0,
        None,
    )
    if handle == INVALID_HANDLE_VALUE or handle == 0xFFFFFFFFFFFFFFFF:
        err = kernel32.GetLastError()
        return None, err

    dcb = DCB()
    dcb.DCBlength = ctypes.sizeof(DCB)
    if kernel32.GetCommState(handle, ctypes.byref(dcb)):
        dcb.BaudRate = baud_rate
        dcb.ByteSize = 8
        dcb.Parity = 0
        dcb.StopBits = 0
        dcb.flags = 1
        kernel32.SetCommState(handle, ctypes.byref(dcb))

    timeouts = COMMTIMEOUTS(100, 0, 500, 0, 500)
    kernel32.SetCommTimeouts(handle, ctypes.byref(timeouts))
    return handle, 0


def detect_receiver_port(check_busy=False):
    """
    Scans common COM ports to find which one is the Node 2 LoRa Receiver.
    Tests configured LORA_PORT first, then COM5, COM8, COM3, COM4, COM6, COM7, COM9, COM10.
    If check_busy=True, returns tuple: (available_port, busy_port)
    """
    configured_port = os.getenv("LORA_PORT")
    candidates = [configured_port] if configured_port else []
    # Test COM5 first (user primary), then COM8, COM3, COM4, COM6, COM7, COM9, COM10
    candidates += ["COM5", "COM8", "COM3", "COM4", "COM6", "COM7", "COM9", "COM10"]

    seen = set()
    ordered_candidates = [c for c in candidates if c and not (c in seen or seen.add(c))]

    busy_port = None
    for p in ordered_candidates:
        handle, err = open_win32_port(p, 115200)
        if handle:
            kernel32.CloseHandle(handle)
            return (p, None) if check_busy else p
        elif err == 5:
            if not busy_port:
                busy_port = p

    return (None, busy_port) if check_busy else None


def scan_and_reconnect_port():
    """
    Scans available COM ports to locate the Node 2 LoRa receiver.
    Returns status dictionary with detection outcome and specific guidance if a port is busy.
    """
    configured_port = os.getenv("LORA_PORT", "COM5")

    # If already connected, report current port
    if LATEST_HARDWARE_STREAM.get("is_connected"):
        active_port = LATEST_HARDWARE_STREAM.get("connected_port") or configured_port
        return {
            "success": True,
            "port": active_port,
            "is_connected": True,
            "message": f"Hardware Gateway is currently active on {active_port} at 115200 baud.",
        }

    port, busy_port = detect_receiver_port(check_busy=True)
    if port:
        LATEST_HARDWARE_STREAM["connected_port"] = port
        return {
            "success": True,
            "port": port,
            "is_connected": LATEST_HARDWARE_STREAM.get("is_connected", False),
            "message": f"Successfully detected available hardware gateway port on {port}.",
        }

    if busy_port:
        return {
            "success": False,
            "port": busy_port,
            "is_connected": False,
            "message": f"Port {busy_port} is busy (locked by another application, such as Arduino IDE or VS Code Serial Monitor). Please close the serial monitor tab and retry.",
        }

    return {
        "success": False,
        "port": None,
        "is_connected": False,
        "message": "No active LoRa receiver detected on scanned ports (COM5, COM8, COM3-10). Check USB cable or close serial monitors.",
    }


def _run_listener_loop(app, db, sensor_readings_table, calculate_ml_fn, ntfy_dispatch_fn, user_model, user_device_model=None):
    """Background worker thread that reads from Node 2 LoRa Receiver and writes to DB."""
    logger.info("[HardwareSerial] Background LoRa listener thread started.")

    while True:
        port = os.getenv("LORA_PORT", "COM5")
        handle, err = open_win32_port(port, 115200)

        # If primary port failed, try auto-detecting
        if not handle:
            if err == 5:
                # Port busy (e.g. Arduino IDE Serial Monitor open)
                logger.warning(
                    f"[HardwareSerial] {port} is busy or locked (Win32 Error 5: Access Denied). "
                    "Make sure the Arduino Serial Monitor or VS Code Port Monitor is CLOSED so ShrimpGuard can access it!"
                )
            port, busy_port = detect_receiver_port(check_busy=True)
            if port:
                handle, err = open_win32_port(port, 115200)
            elif busy_port:
                logger.warning(
                    f"[HardwareSerial] Port {busy_port} is detected but locked (Win32 Error 5: Access Denied). "
                    "Close Arduino IDE / VS Code Serial Monitor so ShrimpGuard can connect."
                )

        if not handle:
            LATEST_HARDWARE_STREAM["is_connected"] = False
            time.sleep(3)
            continue

        LATEST_HARDWARE_STREAM["connected_port"] = port
        LATEST_HARDWARE_STREAM["is_connected"] = True
        logger.info(f"[HardwareSerial] Connected to LoRa Receiver on {port} (115200 baud).")

        line_buffer = b""

        try:
            while True:
                buf = ctypes.create_string_buffer(256)
                bytes_read = wintypes.DWORD()
                success = kernel32.ReadFile(handle, buf, 255, ctypes.byref(bytes_read), None)

                if not success:
                    err = kernel32.GetLastError()
                    if err in (2, 5, 6, 22, 31, 995, 1167):
                        logger.warning(f"[HardwareSerial] Win32 ReadFile error {err} on {port} - hardware disconnected.")
                        break

                if success and bytes_read.value > 0:
                    chunk = buf.raw[:bytes_read.value]
                    line_buffer += chunk

                    while b"\n" in line_buffer:
                        raw_line, line_buffer = line_buffer.split(b"\n", 1)
                        line_str = raw_line.decode("utf-8", errors="replace").strip()
                        if not line_str:
                            continue

                        parsed = parse_telemetry_line(line_str)
                        if parsed:
                            temp = parsed["temperature"]
                            ph = parsed["ph"]
                            dev_id = parsed["device_id"]
                            seq = parsed.get("seq")
                            now_dt = datetime.now()
                            now_str = now_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")

                            # ML Classification
                            try:
                                analysis = calculate_ml_fn(temp, ph)
                                status = analysis["overall_status"]
                            except Exception:
                                status = parsed.get("status_hint") or "Warning"
                                analysis = None

                            # Ingest into DB within Flask app context
                            with app.app_context():
                                try:
                                    from sqlalchemy import insert
                                    target_user = None
                                    if user_device_model:
                                        try:
                                            paired = db.session.query(user_device_model).filter(
                                                user_device_model.device_id == dev_id,
                                                user_device_model.status == "Active",
                                            ).first()
                                            if paired:
                                                target_user = paired.user_email
                                                paired.last_seen = now_dt
                                        except Exception as pe:
                                            logger.debug(f"Device lookup error: {pe}")

                                    if not target_user:
                                        target_user = os.getenv("LORA_DEFAULT_USER_EMAIL", "rio@gmail.com")

                                    db.session.execute(
                                        insert(sensor_readings_table).values(
                                            user_email=target_user,
                                            device_id=dev_id,
                                            ph_level=ph,
                                            temperature=temp,
                                            date=now_str,
                                            status=status,
                                        )
                                    )
                                    db.session.commit()
                                    logger.info(
                                        f"[LoRa SYNC] Ingested Live Sensor Data -> User: {target_user} | Node: {dev_id} | "
                                        f"Temp: {temp:.2f} \u00b0C | pH: {ph:.2f} | Status: {status} (Seq {seq})"
                                    )

                                    # Trigger ntfy alerts on Warning/Critical
                                    if status in ("Critical", "Warning") and ntfy_dispatch_fn:
                                        try:
                                            topics = []
                                            if user_model and target_user:
                                                u = db.session.query(user_model).filter_by(email=target_user).first()
                                                if u and u.ntfy_topic and u.ntfy_topic not in topics:
                                                    topics.append(u.ntfy_topic)
                                            def_topic = os.getenv("NTFY_DEFAULT_TOPIC")
                                            if def_topic and def_topic not in topics:
                                                topics.append(def_topic)

                                            if topics:
                                                threading.Thread(
                                                    target=ntfy_dispatch_fn,
                                                    args=(status, temp, ph, topics),
                                                    daemon=True,
                                                ).start()
                                        except Exception as ne:
                                            logger.debug(f"ntfy alert dispatch error: {ne}")

                                except Exception as dbe:
                                    db.session.rollback()
                                    logger.error(f"[LoRa SYNC] Database insert error: {dbe}")

                            # Update in-memory cache
                            LATEST_HARDWARE_STREAM.update({
                                "temperature": temp,
                                "ph": ph,
                                "device_id": dev_id,
                                "seq": seq,
                                "rssi": parsed.get("rssi"),
                                "snr": parsed.get("snr"),
                                "status": status,
                                "recorded_at": now_str,
                                "last_packet_time": time.time(),
                                "is_connected": True,
                                "connected_port": port,
                            })

                time.sleep(0.04)

        except Exception as exc:
            logger.warning(f"[HardwareSerial] Read error on {port}: {exc}")
        finally:
            kernel32.CloseHandle(handle)
            LATEST_HARDWARE_STREAM["is_connected"] = False
            logger.info(f"[HardwareSerial] Closed connection on {port}. Reconnecting in 3s...")
            time.sleep(3)


def start_hardware_listener(app, db, sensor_readings_table, calculate_ml_fn, ntfy_dispatch_fn, user_model, user_device_model=None):
    """Spawns the background hardware serial reader daemon."""
    t = threading.Thread(
        target=_run_listener_loop,
        args=(app, db, sensor_readings_table, calculate_ml_fn, ntfy_dispatch_fn, user_model, user_device_model),
        daemon=True,
        name="LoRa-Hardware-Serial-Listener",
    )
    t.start()
    return t
