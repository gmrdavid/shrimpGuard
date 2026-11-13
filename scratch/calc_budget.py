categories = {
    'Sensing & Transducer Subsystem': [
        ('DFRobot Gravity Analog pH Sensor (SEN0161)', 5049.00),
        ('DS18B20 Waterproof Digital Temperature Probe', 110.00)
    ],
    'Microcontroller & Wireless Telemetry Subsystem': [
        ('ESP32 Dual-Core Microcontroller Boards (2 units)', 774.08),
        ('SX1278 (RA-02) 433 MHz LoRa Transceiver Modules (2 units)', 788.00)
    ],
    'Local Display, Edge Storage & Alert Subsystem': [
        ('20x4 Character LCD Module with PCF8574 I2C Backpack', 299.00),
        ('10mm High-Luminance Tricolor LED Kit (Red, Green, Yellow)', 180.00),
        ('Grove Active Piezo Buzzer Module', 145.00),
        ('MicroSD Card Adapter Module (SPI Interface)', 129.00),
        ('High-Speed Industrial MicroSD Card (Logging Storage)', 329.00)
    ],
    'Solar Photovoltaic & Energy Harvesting Subsystem': [
        ('50W Monocrystalline Photovoltaic Solar Panel', 1399.74),
        ('12V Auxiliary Photovoltaic Solar Panel', 549.47),
        ('12V 30Ah Lithium Battery Pack', 528.44),
        ('20A Solar Charge Controller (PWM/BMS)', 324.00),
        ('10A Solar Charge Controller (Backup BMS)', 223.00),
        ('LM2596 Dual USB 5V Step-Down Voltage Regulator Module', 167.19),
        ('DC-DC Step-Down Buck Converter Module', 91.00),
        ('MC4 Solar Extension Cable (Pair)', 535.00),
        ('Waterproof MC4 Connectors for Solar Wiring', 245.00)
    ],
    'Electrical Protection, Enclosure & Interconnects': [
        ('AC & DC Dual-Pole Miniature Circuit Breaker (2 units)', 567.58),
        ('Weatherproof Acrylic Storage & Electrical Enclosure Box (2 units)', 642.00),
        ('Grooved Metal DIN Rail (35mm Mounting Bracket)', 143.44),
        ('Cable Waterproof Compression Glands / Connectors', 130.56),
        ('Prototype PCB & Stripboard Breadboards', 280.92),
        ('Terminal Block Screw Wire Connectors', 229.32),
        ('L-Spacer PCB Standoff Mounting Spacers', 188.56),
        ('Resistor Assortment Kit (Current-limiting & Pull-up)', 220.00),
        ('Multi-color Ribbon Jumper Wires (F/F, M/F, M/M packs)', 321.69)
    ],
    'Cloud Deployment & Online Software Infrastructure (1-Year)': [
        ('Railway.app Cloud Hosting & Application Container Deployment ($5/mo)', 3480.00),
        ('Railway Managed MySQL Cloud Relational Database (Persistent Storage)', 1200.00),
        ('Custom Domain Registration & Automated SSL Certificate (1-Year)', 750.00),
        ('ntfy.sh Web Push Notification Telemetry Service (Open-source Tier)', 0.00)
    ]
}

grand_total = 0
hw_total = 0
cloud_total = 0
for cat, items in categories.items():
    sub = sum(p for _, p in items)
    grand_total += sub
    if 'Cloud' not in cat:
        hw_total += sub
    else:
        cloud_total += sub
    print(f"{cat}: PHP {sub:,.2f}")

print("-" * 50)
print(f"Subtotal Hardware (CapEx): PHP {hw_total:,.2f}")
print(f"Subtotal Cloud Deployment (OpEx 1-Yr): PHP {cloud_total:,.2f}")
print(f"GRAND TOTAL SYSTEM INVESTMENT: PHP {grand_total:,.2f}")
