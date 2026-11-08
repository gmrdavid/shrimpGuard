import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

def create_system_architecture_diagram():
    # Canvas setup - high resolution for crystal-clear readability
    fig_w, fig_h = 13.0, 22.0
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Background color
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    # Color definitions (ShrimpGuard design system)
    BRAND_TEAL = "#126b4f"
    BRAND_DARK = "#0a3d2c"

    # Helper function to draw rounded boxes
    def draw_card(x, y, w, h, bg_color, border_color, border_width=1.5, radius=1.2, zorder=2):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0,rounding_size={radius}",
            facecolor=bg_color,
            edgecolor=border_color,
            linewidth=border_width,
            zorder=zorder
        )
        ax.add_patch(box)
        return box

    def draw_subcard(x, y, w, h, bg_color="#ffffff", border_color="#cbd5e1", zorder=3):
        return draw_card(x, y, w, h, bg_color, border_color, border_width=1.0, radius=0.8, zorder=zorder)

    def draw_arrow(x, y_start, y_end, color="#475569", width=2.0):
        ax.annotate(
            "",
            xy=(x, y_end),
            xytext=(x, y_start),
            arrowprops=dict(
                arrowstyle="-|>",
                color=color,
                lw=width,
                mutation_scale=16,
                shrinkA=0,
                shrinkB=0
            ),
            zorder=5
        )

    # =========================================================================
    # HEADER / TITLE
    # =========================================================================
    # Top banner card
    draw_card(3, 96.2, 94, 3.2, "#f0fdf4", BRAND_TEAL, border_width=1.8, radius=0.8)
    ax.text(50, 98.1, "SHRIMPGUARD: END-TO-END SYSTEM ARCHITECTURAL DESIGN",
            ha="center", va="center", fontsize=15, fontweight="heavy", color=BRAND_DARK, family="sans-serif")
    ax.text(50, 96.9, "Autonomous IoT Multi-Node Telemetry, Edge ML Classification & Cloud AI Decision Support for Penaeus vannamei",
            ha="center", va="center", fontsize=9, fontweight="normal", color="#334155", family="sans-serif")

    # =========================================================================
    # LAYER 1: IOT SENSING LAYER (Water Quality Sensors)
    # Y-range: 85.5 to 95.0 (height ~ 9.5)
    # =========================================================================
    draw_card(3, 85.8, 94, 9.4, "#f0f9ff", "#0284c7", border_width=1.5)
    
    # Layer Title & Subtitle
    ax.text(50, 94.2, "1. IOT SENSING LAYER (POND WATER QUALITY PROBES)",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#0369a1", family="sans-serif")
    ax.text(50, 93.1, "Submersible aquaculture electrochemical and thermal probes deployed directly in pond water",
            ha="center", va="center", fontsize=8.5, fontstyle="italic", color="#0284c7", family="sans-serif")

    # 3 Probe Cards
    # Probe 1: DFRobot pH
    draw_subcard(5, 86.6, 28, 5.8, "#ffffff", "#38bdf8")
    ax.text(19, 91.5, "DFRobot Analog pH Sensor", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0f172a")
    ax.text(19, 90.3, "Model: SEN0161 Glass Electrode", ha="center", va="center", fontsize=7.5, color="#0284c7", fontweight="semibold")
    ax.text(19, 89.1, "• Range: 0.00 – 14.00 pH (±0.1 pH)\n• Auto-temp software compensation\n• 2-Point Buffer EEPROM Calibration\n• Connected: ADC1_CH7 (GPIO 35)",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Probe 2: DS18B20 Temp
    draw_subcard(36, 86.6, 28, 5.8, "#ffffff", "#38bdf8")
    ax.text(50, 91.5, "DS18B20 Temperature Sensor", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0f172a")
    ax.text(50, 90.3, "Waterproof Stainless Steel Probe", ha="center", va="center", fontsize=7.5, color="#0284c7", fontweight="semibold")
    ax.text(50, 89.1, "• Range: -55°C to +125°C (±0.5°C)\n• Digital 1-Wire Dallas Bus Protocol\n• 12-bit High Precision Conversion\n• Connected: GPIO 4 (4.7kΩ pull-up)",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Probe 3: Expansion & Water Metrics
    draw_subcard(67, 86.6, 28, 5.8, "#ffffff", "#38bdf8")
    ax.text(81, 91.5, "Calculated Water Parameters", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0f172a")
    ax.text(81, 90.3, "Integrated Physiological Metrics", ha="center", va="center", fontsize=7.5, color="#0284c7", fontweight="semibold")
    ax.text(81, 89.1, "• Free Toxic Ammonia (NH3) Ratio\n• Carbon Dioxide (CO2) Saturation\n• Salinity & Osmoregulatory Bounds\n• Pond Thermal Gradient Analysis",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Arrow 1 -> 2
    draw_arrow(50, 85.8, 84.4)

    # =========================================================================
    # LAYER 2: DEVICE PROCESSING & LOCAL MONITORING (NODE 1 & POWER)
    # Y-range: 72.0 to 84.4 (height ~ 12.4)
    # =========================================================================
    draw_card(3, 72.0, 94, 12.4, "#f0fdf4", "#16a34a", border_width=1.5)
    
    ax.text(50, 83.4, "2. DEVICE PROCESSING & EDGE INTELLIGENCE (NODE 1: POND TRANSMITTER)",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#15803d", family="sans-serif")
    ax.text(50, 82.3, "Floating autonomous pond-side station executing edge ML inference and LoRa telemetry packet broadcast",
            ha="center", va="center", fontsize=8.5, fontstyle="italic", color="#16a34a", family="sans-serif")

    # Left: ESP32 Core Controller
    draw_subcard(5, 73.0, 28, 8.4, "#ffffff", "#4ade80")
    ax.text(19, 80.4, "ESP32 Dev Module (Node 1)", ha="center", va="center", fontsize=10, fontweight="bold", color="#0f172a")
    ax.text(19, 79.2, "Dual-Core Tensilica Xtensa @ 240MHz", ha="center", va="center", fontsize=7.5, color="#16a34a", fontweight="semibold")
    ax.text(19, 76.5, "• 12-Bit Low-Noise SAR ADC\n• Non-blocking hardware timers\n• FreeRTOS task scheduling\n• 5s broadcast interval\n• Deep-sleep power management\n• 3.3V Ultra-low quiescent LDO",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Center: Embedded Edge ML Classifier
    draw_subcard(36, 73.0, 28, 8.4, "#ffffff", "#22c55e")
    ax.text(50, 80.4, "Embedded Edge ML Engine", ha="center", va="center", fontsize=10, fontweight="bold", color="#0f172a")
    ax.text(50, 79.2, "WaterQualityModel.h (Decision Tree)", ha="center", va="center", fontsize=7.5, color="#15803d", fontweight="semibold")
    ax.text(50, 76.5, "• Trained scikit-learn tree on-chip\n• Sub-millisecond instant inference\n• Classifies without cloud dependency:\n   - OPTIMAL (28–32°C, pH 7.5–8.5)\n   - WARNING (Sub-optimal bounds)\n   - CRITICAL (Lethal boundaries)",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Right: Solar Harvester & LoRa Radio TX
    draw_subcard(67, 73.0, 28, 8.4, "#ffffff", "#4ade80")
    ax.text(81, 80.4, "Power & RF Subsystem", ha="center", va="center", fontsize=10, fontweight="bold", color="#0f172a")
    ax.text(81, 79.2, "Autonomous 24/7 Energy & Radio TX", ha="center", va="center", fontsize=7.5, color="#16a34a", fontweight="semibold")
    ax.text(81, 76.5, "• SX1278 Ra-02 LoRa Transceiver\n• 433.5 MHz ISM Chirp Spread Spectrum\n• SPI Bus: NSS=5, SCK=18, MISO=19, MOSI=23\n• 3.7V 18650 Li-ion Battery + BMS\n• Solar PV Panel + MPPT Charger\n• Off-grid continuous pond operation",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Arrow 2 -> 3
    draw_arrow(50, 72.0, 70.6)

    # =========================================================================
    # LAYER 3: COMMUNICATION LAYER (LORA RF LINK & NODE 2 BASE STATION)
    # Y-range: 58.2 to 70.6 (height ~ 12.4)
    # =========================================================================
    draw_card(3, 58.2, 94, 12.4, "#fff7ed", "#ea580c", border_width=1.5)
    
    ax.text(50, 69.6, "3. COMMUNICATION & BASE STATION GATEWAY LAYER (NODE 2)",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#c2410c", family="sans-serif")
    ax.text(50, 68.5, "Long-range Sub-GHz LoRa RF telemetry link and Node 2 field monitoring gateway at farm headquarters",
            ha="center", va="center", fontsize=8.5, fontstyle="italic", color="#ea580c", family="sans-serif")

    # Box 1: LoRa RF Transmission
    draw_subcard(5, 59.2, 28, 8.4, "#ffffff", "#fb923c")
    ax.text(19, 66.6, "Long-Range LoRa RF Link", ha="center", va="center", fontsize=9.8, fontweight="bold", color="#0f172a")
    ax.text(19, 65.4, "433.5 MHz Sub-GHz CSS", ha="center", va="center", fontsize=7.5, color="#c2410c", fontweight="semibold")
    ax.text(19, 62.7, "• 1–5+ km outdoor range over ponds\n• High RF noise immunity (SNR > 9dB)\n• ASCII CSV Packet format:\n  'SG1,NODE01,seq,temp,pH,status'\n• RadioLib non-blocking DIO0 IRQ\n• Zero cellular or SIM card costs",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Box 2: Node 2 Receiver & Base Station
    draw_subcard(36, 59.2, 28, 8.4, "#ffffff", "#f97316")
    ax.text(50, 66.6, "Node 2 Base Station Receiver", ha="center", va="center", fontsize=9.8, fontweight="bold", color="#0f172a")
    ax.text(50, 65.4, "ESP32 Central Gateway Controller", ha="center", va="center", fontsize=7.5, color="#ea580c", fontweight="semibold")
    ax.text(50, 62.7, "• SX1278 433 MHz LoRa Receiver\n• Telemetry validation & CRC check\n• Embedded ML classification fallback\n• Direct USB CDC Serial Bridge\n• Win32 hardware listener @ 115200\n• Packet loss & RSSI signal monitor",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Box 3: Local Field Monitoring (LCD, LEDs, Buzzer)
    draw_subcard(67, 59.2, 28, 8.4, "#ffffff", "#fb923c")
    ax.text(81, 66.6, "Local Field UI & Audio-Visual", ha="center", va="center", fontsize=9.8, fontweight="bold", color="#0f172a")
    ax.text(81, 65.4, "On-Site Hardware Telemetry Output", ha="center", va="center", fontsize=7.5, color="#c2410c", fontweight="semibold")
    ax.text(81, 62.7, "• 20x4 I2C LCD Display (HD44780):\n  Live Temp, pH, Status, RSSI, Seq\n• Tricolor Status LEDs:\n  Green (Optimal), Yellow, Red\n• Active 5V Piezo Acoustic Buzzer:\n  Multi-cadence alarm (Silent/Slow/Fast)",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Arrow 3 -> 4
    draw_arrow(50, 58.2, 56.8)

    # =========================================================================
    # LAYER 4: CLOUD & SERVER INTELLIGENCE LAYER
    # Y-range: 44.4 to 56.8 (height ~ 12.4)
    # =========================================================================
    draw_card(3, 44.4, 94, 12.4, "#faf5ff", "#9333ea", border_width=1.5)
    
    ax.text(50, 55.8, "4. CLOUD & SERVER INTELLIGENCE LAYER (SHRIMPGUARD CORE)",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#7e22ce", family="sans-serif")
    ax.text(50, 54.7, "Flask application server, MySQL relational storage, Scikit-learn ML model, and Google Gemini AI Advisory",
            ha="center", va="center", fontsize=8.5, fontstyle="italic", color="#9333ea", family="sans-serif")

    # Box 1: MySQL & Data Ingestion
    draw_subcard(5, 45.4, 28, 8.4, "#ffffff", "#c084fc")
    ax.text(19, 52.8, "MySQL Relational Database", ha="center", va="center", fontsize=9.8, fontweight="bold", color="#0f172a")
    ax.text(19, 51.6, "Flask-SQLAlchemy Backend Storage", ha="center", va="center", fontsize=7.5, color="#7e22ce", fontweight="semibold")
    ax.text(19, 48.9, "• sensors (ph_level, temperature, status)\n• users (role-based access control)\n• activity_logs (audit & safety logs)\n• aquaculture_calculations (history)\n• Real-time REST API (/api/readings)\n• Automated telemetry data ingestion",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Box 2: Scikit-learn Decision Tree ML
    draw_subcard(36, 45.4, 28, 8.4, "#ffffff", "#a855f7")
    ax.text(50, 52.8, "Machine Learning Classifier", ha="center", va="center", fontsize=9.8, fontweight="bold", color="#0f172a")
    ax.text(50, 51.6, "best_water_quality_model.joblib", ha="center", va="center", fontsize=7.5, color="#6b21a8", fontweight="semibold")
    ax.text(50, 48.9, "• Scikit-learn DecisionTreeClassifier\n• LabelEncoder (Optimal/Warning/Critical)\n• Boundary analysis for Penaeus vannamei:\n   - Temp: 28.0°C – 32.0°C (Set: 30.0°C)\n   - pH: 7.50 – 8.50 (Set: 8.00)\n• Dynamic tolerance & trend analytics",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Box 3: Google Gemini AI Decision Support
    draw_subcard(67, 45.4, 28, 8.4, "#ffffff", "#c084fc")
    ax.text(81, 52.8, "Google Gemini AI Decision Engine", ha="center", va="center", fontsize=9.8, fontweight="bold", color="#0f172a")
    ax.text(81, 51.6, "AI Expert Aquaculture Recommendations", ha="center", va="center", fontsize=7.5, color="#7e22ce", fontweight="semibold")
    ax.text(81, 48.9, "• Domain-tuned shrimp biology reasoning\n• Automated clinical pond diagnoses\n• Step-by-step chemical treatment plans:\n   - Liming (CaCO3 / CaO / NaHCO3)\n   - Molasses / Carbon balance (C:N)\n   - Paddlewheel aeration optimization",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Arrow 4 -> 5
    draw_arrow(50, 44.4, 43.0)

    # =========================================================================
    # LAYER 5: ALERTS AND NOTIFICATIONS SYSTEM
    # Y-range: 30.6 to 43.0 (height ~ 12.4)
    # =========================================================================
    draw_card(3, 30.6, 94, 12.4, "#eef2ff", "#4f46e5", border_width=1.5)
    
    ax.text(50, 42.0, "5. MULTI-TIER ALERTS AND NOTIFICATIONS SYSTEM",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#3730a3", family="sans-serif")
    ax.text(50, 40.9, "Instant multi-channel alerting dispatching audible, visual, cloud push, and in-app emergency warnings",
            ha="center", va="center", fontsize=8.5, fontstyle="italic", color="#4f46e5", family="sans-serif")

    # Alert 1: Physical Local Alerts
    draw_subcard(5, 31.6, 28, 8.4, "#ffffff", "#818cf8")
    ax.text(19, 39.0, "Local Base Station Alerts", ha="center", va="center", fontsize=9.8, fontweight="bold", color="#0f172a")
    ax.text(19, 37.8, "Immediate Physical On-Site Alarms", ha="center", va="center", fontsize=7.5, color="#3730a3", fontweight="semibold")
    ax.text(19, 35.1, "• Tricolor LEDs (Optimal/Warning/Critical)\n• 5V Active Acoustic Buzzer sounder:\n   - Warning: Intermittent 1.2s pulse\n   - Critical: Rapid 5 Hz urgent siren\n   - Timeout: LoRa loss alert (>20s)\n• Immediate warning for pond workers",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Alert 2: ntfy.sh Mobile Push
    draw_subcard(36, 31.6, 28, 8.4, "#ffffff", "#6366f1")
    ax.text(50, 39.0, "ntfy.sh Mobile Cloud Push", ha="center", va="center", fontsize=9.8, fontweight="bold", color="#0f172a")
    ax.text(50, 37.8, "Automated Mobile App & Browser Push", ha="center", va="center", fontsize=7.5, color="#312e81", fontweight="semibold")
    ax.text(50, 35.1, "• Private secure topic (sg-pond-xxxx)\n• Dispatched instantly on Warning/Critical\n• Zero SMS fees or telco SIM overhead\n• iOS / Android lockscreen notification\n• Includes AI biological diagnostic summary\n• Actionable 1-click corrective protocol",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Alert 3: Web Dashboard Alert Center
    draw_subcard(67, 31.6, 28, 8.4, "#ffffff", "#818cf8")
    ax.text(81, 39.0, "Web Dashboard Alert Center", ha="center", va="center", fontsize=9.8, fontweight="bold", color="#0f172a")
    ax.text(81, 37.8, "In-App Telemetry & Notification Hub", ha="center", va="center", fontsize=7.5, color="#3730a3", fontweight="semibold")
    ax.text(81, 35.1, "• Live flash banner on abnormal values\n• Top notification bell with unread badge\n• Incident severity filter (Warning/Crit)\n• Detailed audit log of parameter breaches\n• Timestamped history with AI treatment logs\n• Client & Admin role visibility",
            ha="center", va="center", fontsize=7.2, color="#334155", linespacing=1.2)

    # Arrow 5 -> 6
    draw_arrow(50, 30.6, 29.2)

    # =========================================================================
    # LAYER 6: USER INTERFACE LAYER (SHRIMPGUARD WEB DASHBOARD)
    # Y-range: 15.0 to 29.2 (height ~ 14.2)
    # =========================================================================
    draw_card(3, 15.0, 94, 14.2, "#f0fdfa", "#0d9488", border_width=1.5)
    
    ax.text(50, 28.2, "6. USER INTERFACE LAYER (SHRIMPGUARD RESPONSIVE WEB DASHBOARD)",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#0f766e", family="sans-serif")
    ax.text(50, 27.1, "Full-featured web management platform accessible across desktop, tablet, and mobile devices",
            ha="center", va="center", fontsize=8.5, fontstyle="italic", color="#0d9488", family="sans-serif")

    # 4 Module Cards across UI
    # UI Mod 1: Real-time & Gauge
    draw_subcard(5, 16.0, 21.5, 10.2, "#ffffff", "#2dd4bf")
    ax.text(15.75, 25.1, "Real-Time Monitoring", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(15.75, 23.9, "Live Telemetry Gages", ha="center", va="center", fontsize=7.2, color="#0f766e", fontweight="semibold")
    ax.text(15.75, 20.4, "• Live pH & Temp dials\n• Optimal range bands\n• 5s auto-polling stream\n• Telemetry heartbeat\n• Dynamic status pills\n• Live SVG gauges",
            ha="center", va="center", fontsize=7.0, color="#334155", linespacing=1.25)

    # UI Mod 2: Historical & Calendar
    draw_subcard(28.5, 16.0, 21.5, 10.2, "#ffffff", "#2dd4bf")
    ax.text(39.25, 25.1, "Historical Data", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(39.25, 23.9, "Interactive Trends", ha="center", va="center", fontsize=7.2, color="#0f766e", fontweight="semibold")
    ax.text(39.25, 20.4, "• Calendar date filter\n• Green/red indicators\n  (readings available)\n• Visual Chart.js trends\n• Raw data log tables\n• CSV / PDF export",
            ha="center", va="center", fontsize=7.0, color="#334155", linespacing=1.25)

    # UI Mod 3: Tools & Calculators
    draw_subcard(52.0, 16.0, 21.5, 10.2, "#ffffff", "#2dd4bf")
    ax.text(62.75, 25.1, "Aquaculture Tools", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(62.75, 23.9, "Scientific Calculators", ha="center", va="center", fontsize=7.2, color="#0f766e", fontweight="semibold")
    ax.text(62.75, 20.4, "• Biomass & Feed Calc\n• Toxic Ammonia (NH3)\n• CO2 Saturation Calc\n• Shrimp Growth / FCR\n• Gemini AI insights\n• Vannamei standards",
            ha="center", va="center", fontsize=7.0, color="#334155", linespacing=1.25)

    # UI Mod 4: Hardware & Devices
    draw_subcard(75.5, 16.0, 21.5, 10.2, "#ffffff", "#2dd4bf")
    ax.text(86.25, 25.1, "Devices & Hardware", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(86.25, 23.9, "Hardware Management", ha="center", va="center", fontsize=7.2, color="#0f766e", fontweight="semibold")
    ax.text(86.25, 20.4, "• 10-Unit inventory\n• Online/Offline badges\n• Live COM port gateway\n• Diagnostics test suite\n• LoRa link RSSI / SNR\n• System logs & config",
            ha="center", va="center", fontsize=7.0, color="#334155", linespacing=1.25)

    # Arrow 6 -> 7
    draw_arrow(50, 15.0, 13.6)

    # =========================================================================
    # LAYER 7: USER DECISION MAKING & AQUACULTURE INTERVENTIONS
    # Y-range: 2.8 to 13.6 (height ~ 10.8)
    # =========================================================================
    draw_card(3, 2.8, 94, 10.8, "#f8fafc", "#64748b", border_width=1.5)
    
    ax.text(50, 12.6, "7. USER DECISION MAKING & PRECISION AQUACULTURE INTERVENTIONS",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#1e293b", family="sans-serif")
    ax.text(50, 11.5, "Enables shrimp farm managers to execute timely, scientifically grounded actions for Penaeus vannamei",
            ha="center", va="center", fontsize=8.5, fontstyle="italic", color="#475569", family="sans-serif")

    # 4 Action Pillars
    # Pillar 1: Aeration
    draw_subcard(5, 3.6, 21.5, 7.2, "#ffffff", "#94a3b8")
    ax.text(15.75, 9.6, "Aeration Management", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#0f172a")
    ax.text(15.75, 8.6, "Oxygen & Thermal Mix", ha="center", va="center", fontsize=7.0, color="#2563eb", fontweight="semibold")
    ax.text(15.75, 6.2, "• Modulate paddlewheels\n• Prevent stratification\n• Maintain DO > 5.0 mg/L\n• Lower hyperthermic stress",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Pillar 2: Chemical & pH
    draw_subcard(28.5, 3.6, 21.5, 7.2, "#ffffff", "#94a3b8")
    ax.text(39.25, 9.6, "pH & Alkalinity Dosing", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#0f172a")
    ax.text(39.25, 8.6, "Liming & Buffering", ha="center", va="center", fontsize=7.0, color="#16a34a", fontweight="semibold")
    ax.text(39.25, 6.2, "• Dose CaCO3, CaO, NaHCO3\n• Prevent soft-shell molting\n• Target alkalinity ≥120ppm\n• Stabilize diurnal swings",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Pillar 3: Ammonia & Molasses
    draw_subcard(52.0, 3.6, 21.5, 7.2, "#ffffff", "#94a3b8")
    ax.text(62.75, 9.6, "Toxic NH3 Mitigation", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#0f172a")
    ax.text(62.75, 8.6, "Carbon:Nitrogen Control", ha="center", va="center", fontsize=7.0, color="#ea580c", fontweight="semibold")
    ax.text(62.75, 6.2, "• Apply fermented molasses\n• Stimulate biofloc bacteria\n• Strip unionized NH3 gas\n• Prevent gill damage",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Pillar 4: Feeding & Yield
    draw_subcard(75.5, 3.6, 21.5, 7.2, "#ffffff", "#94a3b8")
    ax.text(86.25, 9.6, "Feeding & Biomass", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#0f172a")
    ax.text(86.25, 8.6, "FCR & Growth Control", ha="center", va="center", fontsize=7.0, color="#7c3aed", fontweight="semibold")
    ax.text(86.25, 6.2, "• Adjust tray feed rations\n• Suppress feed during stress\n• Add Vitamin C & probiotics\n• Maximize survival & ROI",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # =========================================================================
    # BOTTOM CAPTION
    # =========================================================================
    ax.text(50, 1.2, "Figure 3. System Architectural Design — ShrimpGuard IoT, Multi-Node Telemetry & Decision Support Platform",
            ha="center", va="center", fontsize=11, fontweight="bold", color="#0f172a", family="sans-serif")

    # Output paths
    output_png = Path("static/images/system_architecture_diagram.png")
    output_png.parent.mkdir(parents=True, exist_ok=True)
    
    artifact_png = Path(r"C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188\system_architecture_diagram.png")
    
    plt.tight_layout(pad=0.2)
    fig.savefig(output_png, format="png", dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    fig.savefig(artifact_png, format="png", dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    
    print(f"Successfully generated diagram at:\n  - {output_png.resolve()} ({output_png.stat().st_size} bytes)\n  - {artifact_png.resolve()} ({artifact_png.stat().st_size} bytes)")

if __name__ == "__main__":
    create_system_architecture_diagram()
