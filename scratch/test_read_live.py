import ctypes
from ctypes import wintypes
import time
import os

kernel32 = ctypes.windll.kernel32
kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CreateFileW.argtypes = [
    wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
    ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE
]

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3

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

class COMMTIMEOUTS(ctypes.Structure):
    _fields_ = [
        ("ReadIntervalTimeout", wintypes.DWORD),
        ("ReadTotalTimeoutMultiplier", wintypes.DWORD),
        ("ReadTotalTimeoutConstant", wintypes.DWORD),
        ("WriteTotalTimeoutMultiplier", wintypes.DWORD),
        ("WriteTotalTimeoutConstant", wintypes.DWORD),
    ]

port = os.getenv("LORA_PORT", "COM5")
print(f"Opening {port} at 115200 baud...")

h = kernel32.CreateFileW(f"\\\\.\\{port}", GENERIC_READ | GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, None)
if h == -1 or h == 0xFFFFFFFFFFFFFFFF:
    err = kernel32.GetLastError()
    print(f"FAILED to open {port}! Win32 Error: {err}")
    if err == 5:
        print("Error 5: Access Denied. COM5 is locked by another program or hung serial driver.")
        print("ACTION: Unplug the ESP32 USB cable from your PC, wait 2 seconds, and plug it back in.")
    exit(1)

dcb = DCB()
dcb.DCBlength = ctypes.sizeof(DCB)
if kernel32.GetCommState(h, ctypes.byref(dcb)):
    dcb.BaudRate = 115200
    dcb.ByteSize = 8
    dcb.Parity = 0
    dcb.StopBits = 0
    dcb.flags = 1
    kernel32.SetCommState(h, ctypes.byref(dcb))

timeouts = COMMTIMEOUTS(100, 0, 500, 0, 500)
kernel32.SetCommTimeouts(h, ctypes.byref(timeouts))

print(f"SUCCESS: Connected to {port}! Listening for live LoRa packets for 15 seconds...\n")

start_time = time.time()
buffer = b""

while time.time() - start_time < 15:
    buf = ctypes.create_string_buffer(256)
    read_bytes = wintypes.DWORD()
    if kernel32.ReadFile(h, buf, 255, ctypes.byref(read_bytes), None) and read_bytes.value > 0:
        buffer += buf.raw[:read_bytes.value]
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            line_str = line.decode('utf-8', errors='replace').strip()
            if line_str:
                print(f"[COM5 DATA] {line_str}")

kernel32.CloseHandle(h)
print("\nTest completed. Port closed cleanly.")
