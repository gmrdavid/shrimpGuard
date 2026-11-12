import psutil
import socket

for iface_name, addrs in psutil.net_if_addrs().items():
    for addr in addrs:
        if addr.family == socket.AF_INET:
            print(f"Interface: {iface_name} -> IP: {addr.address} (Netmask: {addr.netmask})")
