import ctypes
from ctypes import wintypes

kernel32 = ctypes.windll.kernel32

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3

print("Test 1: Without setting restype:")
h1 = kernel32.CreateFileW(r"\\.\COM5", GENERIC_READ | GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, None)
err1 = kernel32.GetLastError()
print(f"h1 = {h1} (type: {type(h1)}), err1 = {err1}")

print("\nTest 2: WITH setting restype to c_void_p and argtypes:")
kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CreateFileW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    ctypes.c_void_p,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HANDLE
]
h2 = kernel32.CreateFileW(r"\\.\COM5", GENERIC_READ | GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, None)
err2 = kernel32.GetLastError()
print(f"h2 = {h2} (type: {type(h2)}), err2 = {err2}")
if h2 and h2 != -1 and h2 != 0xFFFFFFFFFFFFFFFF:
    print("SUCCESS! COM5 IS ACTUALLY OPEN!")
    kernel32.CloseHandle(h2)
