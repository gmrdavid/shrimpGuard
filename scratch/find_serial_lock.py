import psutil
import os

print("Scanning processes...")
target_keywords = ["python", "arduino", "code", "serial", "putty", "screen", "shrimpguard"]
found = []
for p in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        pname = p.info['name'].lower()
        cmd = " ".join(p.info['cmdline'] or []).lower()
        for kw in target_keywords:
            if kw in pname or kw in cmd:
                found.append((p.info['pid'], p.info['name'], cmd[:80]))
                break
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

for pid, name, cmd in found:
    print(f"PID {pid:6d} | {name:20s} | {cmd}")
