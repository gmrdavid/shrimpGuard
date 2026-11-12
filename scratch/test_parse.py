import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from hardware_serial import parse_telemetry_line

line1 = '[RX] OK  Node=NODE01 | Seq=1 | Temp=28.52 C | pH=7.82 | Status=Optimal | RSSI=-65 dBm | SNR=8.5 dB'
line2 = 'LORA_JSON:{"device":"NODE01","seq":1,"temperature":28.52,"ph":7.82,"status":"Optimal","rssi":-65.0,"snr":8.5}'
line3 = 'SG1,NODE01,1,28.52,7.82,Optimal'

print('Test 1 (Diagnostic):', parse_telemetry_line(line1))
print('Test 2 (JSON):', parse_telemetry_line(line2))
print('Test 3 (CSV):', parse_telemetry_line(line3))
