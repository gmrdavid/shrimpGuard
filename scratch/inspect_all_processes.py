import psutil

print(f"{'PID':>7} | {'NAME':30} | {'USERNAME':25} | COMMAND")
print("-" * 100)
for p in psutil.process_iter(['pid', 'name', 'username', 'cmdline']):
    try:
        pid = p.info['pid']
        name = p.info['name'] or ''
        user = p.info['username'] or ''
        cmd = ' '.join(p.info['cmdline'] or [])
        print(f"{pid:7d} | {name:30s} | {user:25s} | {cmd[:60]}")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
