import psutil
import os

print(f"Current PID: {os.getpid()}")

matches = []
for p in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        pname = p.info['name'].lower()
        cmd = " ".join(p.info['cmdline'] or []).lower()
        if any(k in pname or k in cmd for k in ['python', 'arduino', 'serial', 'putty', 'node', 'esptool', 'shrimp', 'flask']):
            matches.append((p.info['pid'], p.info['name'], cmd[:120]))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

print(f"Found {len(matches)} relevant processes:")
for pid, name, cmd in matches:
    print(f"PID {pid:6d} | {name:20s} | {cmd}")
