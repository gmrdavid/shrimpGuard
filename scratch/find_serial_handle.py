import ctypes
from ctypes import wintypes
import sys
import psutil

ntdll = ctypes.windll.ntdll
kernel32 = ctypes.windll.kernel32

STATUS_INFO_LENGTH_MISMATCH = 0xC0000004
SystemHandleInformation = 16

class SYSTEM_HANDLE_TABLE_ENTRY_INFO(ctypes.Structure):
    _fields_ = [
        ("UniqueProcessId", wintypes.USHORT),
        ("CreatorBackTraceIndex", wintypes.USHORT),
        ("ObjectTypeIndex", ctypes.c_ubyte),
        ("HandleAttributes", ctypes.c_ubyte),
        ("HandleValue", wintypes.USHORT),
        ("Object", ctypes.c_void_p),
        ("GrantedAccess", wintypes.ULONG),
    ]

# Let's inspect processes that might touch serial ports:
# VS Code extensions, Arduino, Node, etc.
candidates = []
for p in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmd = ' '.join(p.info['cmdline'] or []).lower()
        name = (p.info['name'] or '').lower()
        if any(x in cmd or x in name for x in ['serial', 'monitor', 'arduino', 'code', 'node']):
            candidates.append((p.info['pid'], p.info['name'], cmd[:100]))
    except Exception:
        pass

print(f"Found {len(candidates)} candidates:")
for pid, name, cmd in candidates:
    print(f"  PID {pid:5d} | {name:20s} | {cmd}")
