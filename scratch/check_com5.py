import ctypes
from ctypes import wintypes

kernel32 = ctypes.windll.kernel32

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = -1

port = r"\\.\COM5"
handle = kernel32.CreateFileW(
    port,
    GENERIC_READ | GENERIC_WRITE,
    0,  # exclusive access
    None,
    OPEN_EXISTING,
    0,
    None
)

if handle == INVALID_HANDLE_VALUE or handle == 0xFFFFFFFFFFFFFFFF:
    err = kernel32.GetLastError()
    print(f"COM5 is LOCKED/UNAVAILABLE! Win32 Error Code: {err}")
    if err == 5:
        print("Error 5 = ERROR_ACCESS_DENIED: Another application is currently holding COM5 open!")
    elif err == 2:
        print("Error 2 = ERROR_FILE_NOT_FOUND: COM5 is not plugged in or doesn't exist.")
    else:
        print(f"Unknown error: {err}")
else:
    print("COM5 is OPEN and AVAILABLE! (No other process is locking it right now)")
    kernel32.CloseHandle(handle)
