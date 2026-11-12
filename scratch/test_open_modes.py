import ctypes
from ctypes import wintypes

kernel32 = ctypes.windll.kernel32

kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CreateFileW.argtypes = [
    wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
    ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE
]

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
FILE_SHARE_READ = 1
FILE_SHARE_WRITE = 2

modes = [
    ("READ/WRITE, Share 0", GENERIC_READ | GENERIC_WRITE, 0),
    ("READ ONLY, Share 0", GENERIC_READ, 0),
    ("WRITE ONLY, Share 0", GENERIC_WRITE, 0),
    ("READ/WRITE, Share R/W", GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE),
    ("READ ONLY, Share R/W", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE),
    ("NO ACCESS (0), Share 0", 0, 0),
    ("NO ACCESS (0), Share R/W", 0, FILE_SHARE_READ | FILE_SHARE_WRITE),
]

for desc, access, share in modes:
    h = kernel32.CreateFileW(r"\\.\COM5", access, share, None, OPEN_EXISTING, 0, None)
    err = kernel32.GetLastError()
    if h and h != -1 and h != 0xFFFFFFFFFFFFFFFF:
        print(f"{desc}: SUCCESS! Handle = {h}")
        kernel32.CloseHandle(h)
    else:
        print(f"{desc}: FAILED with Error {err}")
