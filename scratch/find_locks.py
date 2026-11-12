import psutil

print("Scanning processes...")
found = []
for p in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        name = (p.info['name'] or '').lower()
        cmd = ' '.join(p.info['cmdline'] or []).lower()
        if any(k in name for k in ['python', 'arduino', 'serial', 'putty', 'monitor', 'code']):
            found.append((p.info['pid'], p.info['name'], cmd[:120]))
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

for pid, name, cmd in found:
    print(f"PID {pid:6d} | {name:20s} | {cmd}")
