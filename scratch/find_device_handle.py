import ctypes
from ctypes import wintypes
import psutil

ntdll = ctypes.windll.ntdll
kernel32 = ctypes.windll.kernel32

SystemExtendedHandleInformation = 64
STATUS_INFO_LENGTH_MISMATCH = 0xC0000004

class SYSTEM_HANDLE_TABLE_ENTRY_INFO_EX(ctypes.Structure):
    _fields_ = [
        ("Object", ctypes.c_void_p),
        ("UniqueProcessId", ctypes.c_size_t),
        ("HandleValue", ctypes.c_size_t),
        ("GrantedAccess", wintypes.ULONG),
        ("CreatorBackTraceIndex", wintypes.USHORT),
        ("ObjectTypeIndex", wintypes.USHORT),
        ("HandleAttributes", wintypes.ULONG),
        ("Reserved", wintypes.ULONG),
    ]

# Let's test checking handles of candidates directly using DuplicateHandle:
current_process = kernel32.GetCurrentProcess()

for p in psutil.process_iter(['pid', 'name']):
    pid = p.info['pid']
    name = p.info['name']
    if pid <= 4:
        continue
    h_proc = kernel32.OpenProcess(0x0040, False, pid) # PROCESS_DUP_HANDLE
    if not h_proc:
        continue
    
    # Try duplicating candidate handle values (multiples of 4 up to 4000)
    for handle_val in range(4, 2000, 4):
        dup_handle = wintypes.HANDLE()
        res = kernel32.DuplicateHandle(
            h_proc,
            wintypes.HANDLE(handle_val),
            current_process,
            ctypes.byref(dup_handle),
            0,
            False,
            2 # DUPLICATE_SAME_ACCESS
        )
        if res and dup_handle.value:
            # Check if this handle is a comm / serial device
            comm_time = ctypes.create_string_buffer(40)
            # GetCommTimeouts returns TRUE only for communication devices (serial ports)!
            if kernel32.GetCommTimeouts(dup_handle, comm_time):
                print(f"FOUND SERIAL PORT HANDLE! PID: {pid} ({name}), Handle: {handle_val}")
            kernel32.CloseHandle(dup_handle)
    kernel32.CloseHandle(h_proc)

print("Scan complete.")
