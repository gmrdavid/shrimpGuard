import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from PIL import Image

def build_advanced_architecture_diagram():
    # Dimensions: 14 inches x 25 inches @ 200 DPI -> 2800 x 5000 px
    fig, ax = plt.subplots(figsize=(14.0, 25.0), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")

    BRAND_TEAL = "#126b4f"
    BRAND_DARK = "#093325"

    def draw_card(x, y, w, h, bg_color, border_color, border_width=1.8, radius=1.0, zorder=2):
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

    def draw_subcard(x, y, w, h, bg_color="#ffffff", border_color="#cbd5e1", border_width=1.2, radius=0.6, zorder=3):
        return draw_card(x, y, w, h, bg_color, border_color, border_width=border_width, radius=radius, zorder=zorder)

    def draw_arrow(x, y_start, y_end, color="#64748b", width=2.2):
        ax.annotate(
            "",
            xy=(x, y_end),
            xytext=(x, y_start),
            arrowprops=dict(
                arrowstyle="-|>",
                color=color,
                lw=width,
                mutation_scale=18,
                shrinkA=0,
                shrinkB=0
            ),
            zorder=6
        )

    def embed_crop(name, x, y, w, h, zorder=4):
        crop_path = Path(f"scratch/crops/{name}.png")
        if crop_path.exists():
            img = Image.open(crop_path)
            ax.imshow(img, extent=(x, x + w, y, y + h), aspect="auto", zorder=zorder)

    # =========================================================================
    # HEADER / BANNER
    # =========================================================================
    draw_card(3, 96.2, 94, 3.2, "#f0fdf4", BRAND_TEAL, border_width=2.0, radius=0.8)
    ax.text(50, 98.1, "SHRIMPGUARD: SYSTEM ARCHITECTURAL DESIGN",
            ha="center", va="center", fontsize=15.5, fontweight="bold", color=BRAND_DARK, family="sans-serif")
    ax.text(50, 96.9, "Multi-Node LoRa Telemetry, Edge ML Classification & Cloud AI Decision Support for Penaeus vannamei",
            ha="center", va="center", fontsize=9.2, fontweight="normal", color="#1e293b", family="sans-serif")

    # =========================================================================
    # LAYER 1: IOT SENSING LAYER
    # Y-range: 85.6 to 95.2 (height: 9.6)
    # =========================================================================
    draw_card(3, 85.6, 94, 9.6, "#f0f9ff", "#0284c7", border_width=1.6)
    ax.text(50, 94.3, "1. IOT SENSING LAYER (WATER QUALITY SENSORS)",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#0369a1", family="sans-serif")
    ax.text(50, 93.3, "Submersible aquaculture electrochemical and thermal probes deployed directly in pond water",
            ha="center", va="center", fontsize=8.2, fontstyle="italic", color="#0284c7", family="sans-serif")

    # Probe 1: DFRobot pH Sensor
    draw_subcard(5, 86.4, 28, 6.2, "#ffffff", "#38bdf8")
    embed_crop("ph_sensor", 6, 86.8, 5.5, 5.4)
    ax.text(20.5, 91.6, "DFRobot Analog pH Sensor", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(20.5, 90.5, "SEN0161 Glass Electrode • ADC1_CH7", ha="center", va="center", fontsize=7.2, color="#0284c7", fontweight="bold")
    ax.text(20.5, 88.5, "• Range: 0.00 – 14.00 pH (±0.1 pH)\n• Auto-temp software compensation\n• 2-Point Buffer EEPROM Calibration\n• Connected: ESP32 GPIO 35 (ADC)",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Probe 2: DS18B20 Temp Sensor
    draw_subcard(36, 86.4, 28, 6.2, "#ffffff", "#38bdf8")
    embed_crop("temp_sensor", 37, 86.8, 6.0, 5.4)
    ax.text(52.5, 91.6, "DS18B20 Temperature Sensor", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(52.5, 90.5, "Waterproof Thermal Probe • 1-Wire", ha="center", va="center", fontsize=7.2, color="#0284c7", fontweight="bold")
    ax.text(52.5, 88.5, "• Range: -55°C to +125°C (±0.5°C)\n• Digital 1-Wire Dallas Bus Protocol\n• 12-bit High Precision Conversion\n• Connected: ESP32 GPIO 4 (4.7kΩ)",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Probe 3: Expansion & Water Metrics
    draw_subcard(67, 86.4, 28, 6.2, "#ffffff", "#38bdf8")
    ax.text(81, 91.6, "Calculated Water Parameters", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(81, 90.5, "Physiological Quality Metrics", ha="center", va="center", fontsize=7.2, color="#0284c7", fontweight="bold")
    ax.text(81, 88.5, "• Free Toxic Ammonia (NH3) Ratio\n• Carbon Dioxide (CO2) Saturation\n• Salinity & Osmoregulatory Bounds\n• Pond Thermal Stratification Index",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Arrow 1 -> 2
    draw_arrow(50, 85.6, 84.4)

    # =========================================================================
    # LAYER 2: DEVICE PROCESSING & LOCAL MONITORING (NODE 1 & POWER)
    # Y-range: 71.8 to 84.4 (height: 12.6)
    # =========================================================================
    draw_card(3, 71.8, 94, 12.6, "#f0fdf4", "#16a34a", border_width=1.6)
    ax.text(50, 83.4, "2. DEVICE PROCESSING & EDGE INTELLIGENCE (NODE 1: POND TRANSMITTER)",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#15803d", family="sans-serif")
    ax.text(50, 82.4, "Floating autonomous pond-side station executing edge ML inference and LoRa telemetry packet broadcast",
            ha="center", va="center", fontsize=8.2, fontstyle="italic", color="#16a34a", family="sans-serif")

    # Left: ESP32 Core Controller
    draw_subcard(5, 72.6, 28, 9.0, "#ffffff", "#4ade80")
    embed_crop("esp32", 6, 73.6, 5.0, 7.2)
    ax.text(20, 80.5, "ESP32 Dev Module (Node 1)", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(20, 79.4, "Dual-Core Xtensa @ 240MHz", ha="center", va="center", fontsize=7.2, color="#16a34a", fontweight="bold")
    ax.text(20, 76.5, "• 12-Bit Low-Noise SAR ADC\n• Non-blocking hardware timers\n• FreeRTOS task scheduling\n• 5s broadcast cadence\n• Deep-sleep power management\n• Ultra-low quiescent 3.3V rail",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Center: Embedded Edge ML Classifier
    draw_subcard(36, 72.6, 28, 9.0, "#ffffff", "#22c55e")
    embed_crop("ml_brain", 37, 74.2, 5.5, 5.5)
    ax.text(52, 80.5, "Embedded Edge ML Engine", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(52, 79.4, "WaterQualityModel.h (Decision Tree)", ha="center", va="center", fontsize=7.2, color="#15803d", fontweight="bold")
    ax.text(52, 76.5, "• Trained scikit-learn tree on-chip\n• Sub-millisecond instant inference\n• Classifies without cloud dependency:\n   - OPTIMAL (28–32°C, pH 7.5–8.5)\n   - WARNING (Sub-optimal bounds)\n   - CRITICAL (Lethal boundaries)",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Right: Solar Harvester & LoRa Radio TX
    draw_subcard(67, 72.6, 28, 9.0, "#ffffff", "#4ade80")
    embed_crop("lora_module", 68, 74.2, 6.0, 5.5)
    ax.text(82.5, 80.5, "Power & RF Subsystem", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(82.5, 79.4, "Autonomous 24/7 Energy & Radio TX", ha="center", va="center", fontsize=7.2, color="#16a34a", fontweight="bold")
    ax.text(82.5, 76.5, "• SX1278 Ra-02 LoRa Transceiver\n• 433.5 MHz Chirp Spread Spectrum\n• SPI Bus: NSS=5, SCK=18, MOSI=23\n• 3.7V 18650 Li-ion Battery + BMS\n• Solar PV Panel + Charge Controller\n• Off-grid continuous pond operation",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Arrow 2 -> 3
    draw_arrow(50, 71.8, 70.6)

    # =========================================================================
    # LAYER 3: COMMUNICATION LAYER (LORA LINK & NODE 2 BASE STATION)
    # Y-range: 58.0 to 70.6 (height: 12.6)
    # =========================================================================
    draw_card(3, 58.0, 94, 12.6, "#fff7ed", "#ea580c", border_width=1.6)
    ax.text(50, 69.6, "3. COMMUNICATION & BASE STATION GATEWAY LAYER (NODE 2)",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#c2410c", family="sans-serif")
    ax.text(50, 68.6, "Long-range Sub-GHz LoRa RF telemetry link and Node 2 field monitoring gateway at farm headquarters",
            ha="center", va="center", fontsize=8.2, fontstyle="italic", color="#ea580c", family="sans-serif")

    # Subcard 1: LoRa RF Link
    draw_subcard(5, 58.8, 28, 9.0, "#ffffff", "#fb923c")
    embed_crop("lora_antenna", 6, 60.5, 5.5, 5.5)
    ax.text(20, 66.8, "Long-Range LoRa RF Link", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(20, 65.7, "433.5 MHz Sub-GHz CSS", ha="center", va="center", fontsize=7.2, color="#c2410c", fontweight="bold")
    ax.text(20, 62.8, "• 1–5+ km outdoor range over ponds\n• High RF noise immunity (SNR > 9dB)\n• ASCII CSV Packet format:\n  'SG1,NODE01,seq,temp,pH,status'\n• RadioLib non-blocking DIO0 IRQ\n• Zero cellular or SIM card costs",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Subcard 2: Node 2 Base Station Receiver
    draw_subcard(36, 58.8, 28, 9.0, "#ffffff", "#f97316")
    embed_crop("lora_gateway", 37, 60.5, 6.0, 5.5)
    ax.text(52, 66.8, "Node 2 Base Station Receiver", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(52, 65.7, "ESP32 Central Gateway Controller", ha="center", va="center", fontsize=7.2, color="#ea580c", fontweight="bold")
    ax.text(52, 62.8, "• SX1278 433 MHz LoRa Receiver\n• Telemetry validation & CRC check\n• Embedded ML classification fallback\n• Direct USB CDC Serial Bridge\n• Win32 hardware listener @ 115200\n• Packet loss & RSSI signal monitor",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Subcard 3: Local Field Monitoring (LCD, LEDs, Buzzer)
    draw_subcard(67, 58.8, 28, 9.0, "#ffffff", "#fb923c")
    embed_crop("lcd", 68, 63.5, 5.5, 3.5)
    embed_crop("leds", 68, 59.5, 2.5, 3.5)
    embed_crop("buzzer", 71, 59.5, 2.5, 3.2)
    ax.text(83, 66.8, "Local Field UI & Audio-Visual", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(83, 65.7, "On-Site Hardware Telemetry Output", ha="center", va="center", fontsize=7.2, color="#c2410c", fontweight="bold")
    ax.text(83, 62.5, "• 20x4 I2C LCD Display (HD44780):\n  Live Temp, pH, Status, RSSI, Seq\n• Tricolor Status LEDs:\n  Green (Optimal), Yellow, Red\n• Active 5V Piezo Acoustic Buzzer:\n  Multi-cadence alarm (Silent/Slow/Fast)",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Arrow 3 -> 4
    draw_arrow(50, 58.0, 56.8)

    # =========================================================================
    # LAYER 4: CLOUD & SERVER INTELLIGENCE LAYER
    # Y-range: 44.2 to 56.8 (height: 12.6)
    # =========================================================================
    draw_card(3, 44.2, 94, 12.6, "#faf5ff", "#9333ea", border_width=1.6)
    ax.text(50, 55.8, "4. CLOUD & SERVER INTELLIGENCE LAYER (SHRIMPGUARD CORE)",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#7e22ce", family="sans-serif")
    ax.text(50, 54.8, "Flask application server, MySQL relational storage, Scikit-learn ML model, and Google Gemini AI Advisory",
            ha="center", va="center", fontsize=8.2, fontstyle="italic", color="#9333ea", family="sans-serif")

    # Box 1: MySQL & Data Ingestion
    draw_subcard(5, 45.0, 28, 9.0, "#ffffff", "#c084fc")
    embed_crop("cloud_db", 6, 46.8, 5.5, 5.5)
    ax.text(20, 53.0, "MySQL Relational Database", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(20, 51.9, "Flask-SQLAlchemy Backend Storage", ha="center", va="center", fontsize=7.2, color="#7e22ce", fontweight="bold")
    ax.text(20, 49.0, "• sensors (ph_level, temperature, status)\n• users (role-based access control)\n• activity_logs (audit & safety logs)\n• aquaculture_calculations (history)\n• Real-time REST API (/api/readings)\n• Automated telemetry data ingestion",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Box 2: Scikit-learn Decision Tree ML
    draw_subcard(36, 45.0, 28, 9.0, "#ffffff", "#a855f7")
    embed_crop("ml_brain", 37, 46.8, 5.5, 5.5)
    ax.text(52, 53.0, "Machine Learning Classifier", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(52, 51.9, "best_water_quality_model.joblib", ha="center", va="center", fontsize=7.2, color="#6b21a8", fontweight="bold")
    ax.text(52, 49.0, "• Scikit-learn DecisionTreeClassifier\n• LabelEncoder (Optimal/Warning/Critical)\n• Boundary analysis for Penaeus vannamei:\n   - Temp: 28.0°C – 32.0°C (Set: 30.0°C)\n   - pH: 7.50 – 8.50 (Set: 8.00)\n• Dynamic tolerance & trend analytics",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Box 3: Google Gemini AI Decision Support
    draw_subcard(67, 45.0, 28, 9.0, "#ffffff", "#c084fc")
    embed_crop("ai_head", 68, 46.8, 5.5, 5.5)
    ax.text(82, 53.0, "Google Gemini AI Decision Engine", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(82, 51.9, "AI Expert Aquaculture Recommendations", ha="center", va="center", fontsize=7.2, color="#7e22ce", fontweight="bold")
    ax.text(82, 49.0, "• Domain-tuned shrimp biology reasoning\n• Automated clinical pond diagnoses\n• Step-by-step chemical treatment plans:\n   - Liming (CaCO3 / CaO / NaHCO3)\n   - Molasses / Carbon balance (C:N)\n   - Paddlewheel aeration optimization",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Arrow 4 -> 5
    draw_arrow(50, 44.2, 43.0)

    # =========================================================================
    # LAYER 5: ALERTS AND NOTIFICATIONS SYSTEM
    # Y-range: 30.4 to 43.0 (height: 12.6)
    # =========================================================================
    draw_card(3, 30.4, 94, 12.6, "#eef2ff", "#4f46e5", border_width=1.6)
    ax.text(50, 42.0, "5. MULTI-TIER ALERTS AND NOTIFICATIONS SYSTEM",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#3730a3", family="sans-serif")
    ax.text(50, 41.0, "Instant multi-channel alerting dispatching audible, visual, cloud push, and in-app emergency warnings",
            ha="center", va="center", fontsize=8.2, fontstyle="italic", color="#4f46e5", family="sans-serif")

    # Alert 1: Physical Local Alerts
    draw_subcard(5, 31.2, 28, 9.0, "#ffffff", "#818cf8")
    embed_crop("leds", 6, 34.5, 2.5, 4.0)
    embed_crop("buzzer", 9, 34.5, 3.0, 3.5)
    ax.text(21, 39.2, "Local Base Station Alerts", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(21, 38.1, "Immediate Physical On-Site Alarms", ha="center", va="center", fontsize=7.2, color="#3730a3", fontweight="bold")
    ax.text(21, 35.2, "• Tricolor LEDs (Optimal/Warning/Critical)\n• 5V Active Acoustic Buzzer sounder:\n   - Warning: Intermittent 1.2s pulse\n   - Critical: Rapid 5 Hz urgent siren\n   - Timeout: LoRa loss alert (>20s)\n• Immediate warning for pond workers",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Alert 2: ntfy.sh Mobile Push
    draw_subcard(36, 31.2, 28, 9.0, "#ffffff", "#6366f1")
    embed_crop("ntfy_phone", 37, 33.5, 5.0, 4.5)
    ax.text(52, 39.2, "ntfy.sh Mobile Cloud Push", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(52, 38.1, "Automated Mobile App & Browser Push", ha="center", va="center", fontsize=7.2, color="#312e81", fontweight="bold")
    ax.text(52, 35.2, "• Private secure topic (sg-pond-xxxx)\n• Dispatched instantly on Warning/Critical\n• Zero SMS fees or telco SIM overhead\n• iOS / Android lockscreen notification\n• Includes AI biological diagnostic summary\n• Actionable 1-click corrective protocol",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Alert 3: Web Dashboard Alert Center
    draw_subcard(67, 31.2, 28, 9.0, "#ffffff", "#818cf8")
    embed_crop("system_alert_bell", 68, 33.5, 5.0, 4.5)
    ax.text(82, 39.2, "Web Dashboard Alert Center", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(82, 38.1, "In-App Telemetry & Notification Hub", ha="center", va="center", fontsize=7.2, color="#3730a3", fontweight="bold")
    ax.text(82, 35.2, "• Live flash banner on abnormal values\n• Top notification bell with unread badge\n• Incident severity filter (Warning/Crit)\n• Detailed audit log of parameter breaches\n• Timestamped history with AI treatment logs\n• Client & Admin role visibility",
            ha="center", va="center", fontsize=6.8, color="#334155", linespacing=1.2)

    # Arrow 5 -> 6
    draw_arrow(50, 30.4, 29.2)

    # =========================================================================
    # LAYER 6: USER INTERFACE LAYER (SHRIMPGUARD WEB DASHBOARD)
    # Y-range: 15.0 to 29.2 (height: 14.2)
    # =========================================================================
    draw_card(3, 15.0, 94, 14.2, "#f0fdfa", "#0d9488", border_width=1.6)
    ax.text(50, 28.2, "6. USER INTERFACE LAYER (SHRIMPGUARD RESPONSIVE WEB DASHBOARD)",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#0f766e", family="sans-serif")
    ax.text(50, 27.2, "Full-featured web management platform accessible across desktop, tablet, and mobile devices",
            ha="center", va="center", fontsize=8.2, fontstyle="italic", color="#0d9488", family="sans-serif")

    # 4 Module Cards across UI
    # UI Mod 1: Real-time & Gauge
    draw_subcard(5, 15.8, 21.5, 10.5, "#ffffff", "#2dd4bf")
    embed_crop("ui_realtime", 13.5, 21.8, 4.5, 4.0)
    ax.text(15.75, 20.8, "Real-Time Monitoring", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#0f172a")
    ax.text(15.75, 19.8, "Live Telemetry Gages", ha="center", va="center", fontsize=7.0, color="#0f766e", fontweight="bold")
    ax.text(15.75, 17.6, "• Live pH & Temp dials\n• Optimal range bands\n• 5s auto-polling stream\n• Telemetry heartbeat\n• Dynamic status pills\n• Live SVG gauges",
            ha="center", va="center", fontsize=6.6, color="#334155", linespacing=1.2)

    # UI Mod 2: Historical & Calendar
    draw_subcard(28.5, 15.8, 21.5, 10.5, "#ffffff", "#2dd4bf")
    embed_crop("ui_history", 37.0, 21.8, 4.5, 4.0)
    ax.text(39.25, 20.8, "Historical Data", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#0f172a")
    ax.text(39.25, 19.8, "Interactive Trends", ha="center", va="center", fontsize=7.0, color="#0f766e", fontweight="bold")
    ax.text(39.25, 17.6, "• Calendar date filter\n• Green/red indicators\n  (readings available)\n• Visual Chart.js trends\n• Raw data log tables\n• CSV / PDF export",
            ha="center", va="center", fontsize=6.6, color="#334155", linespacing=1.2)

    # UI Mod 3: Tools & Calculators
    draw_subcard(52.0, 15.8, 21.5, 10.5, "#ffffff", "#2dd4bf")
    embed_crop("ui_ml", 60.5, 21.8, 4.5, 4.0)
    ax.text(62.75, 20.8, "Aquaculture Tools", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#0f172a")
    ax.text(62.75, 19.8, "Scientific Calculators", ha="center", va="center", fontsize=7.0, color="#0f766e", fontweight="bold")
    ax.text(62.75, 17.6, "• Biomass & Feed Calc\n• Toxic Ammonia (NH3)\n• CO2 Saturation Calc\n• Shrimp Growth / FCR\n• Gemini AI insights\n• Vannamei standards",
            ha="center", va="center", fontsize=6.6, color="#334155", linespacing=1.2)

    # UI Mod 4: Hardware & Devices
    draw_subcard(75.5, 15.8, 21.5, 10.5, "#ffffff", "#2dd4bf")
    embed_crop("ui_alerts", 84.0, 21.8, 4.5, 4.0)
    ax.text(86.25, 20.8, "Devices & Hardware", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#0f172a")
    ax.text(86.25, 19.8, "Hardware Management", ha="center", va="center", fontsize=7.0, color="#0f766e", fontweight="bold")
    ax.text(86.25, 17.6, "• 10-Unit inventory\n• Online/Offline badges\n• Live COM port gateway\n• Diagnostics test suite\n• LoRa link RSSI / SNR\n• System logs & config",
            ha="center", va="center", fontsize=6.6, color="#334155", linespacing=1.2)

    # Arrow 6 -> 7
    draw_arrow(50, 15.0, 13.6)

    # =========================================================================
    # LAYER 7: USER DECISION MAKING & AQUACULTURE INTERVENTIONS
    # Y-range: 2.8 to 13.6 (height: 10.8)
    # =========================================================================
    draw_card(3, 2.8, 94, 10.8, "#f8fafc", "#64748b", border_width=1.6)
    ax.text(50, 12.6, "7. USER DECISION MAKING & PRECISION AQUACULTURE INTERVENTIONS",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#1e293b", family="sans-serif")
    ax.text(50, 11.6, "Enables shrimp farm managers to execute timely, scientifically grounded actions for Penaeus vannamei",
            ha="center", va="center", fontsize=8.2, fontstyle="italic", color="#475569", family="sans-serif")

    # 4 Action Pillars
    # Pillar 1: Aeration
    draw_subcard(5, 3.6, 21.5, 7.2, "#ffffff", "#94a3b8")
    ax.text(15.75, 9.6, "Aeration Management", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#0f172a")
    ax.text(15.75, 8.6, "Oxygen & Thermal Mix", ha="center", va="center", fontsize=7.0, color="#2563eb", fontweight="bold")
    ax.text(15.75, 6.2, "• Modulate paddlewheels\n• Prevent stratification\n• Maintain DO > 5.0 mg/L\n• Lower hyperthermic stress",
            ha="center", va="center", fontsize=6.6, color="#334155", linespacing=1.2)

    # Pillar 2: Chemical & pH
    draw_subcard(28.5, 3.6, 21.5, 7.2, "#ffffff", "#94a3b8")
    ax.text(39.25, 9.6, "pH & Alkalinity Dosing", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#0f172a")
    ax.text(39.25, 8.6, "Liming & Buffering", ha="center", va="center", fontsize=7.0, color="#16a34a", fontweight="bold")
    ax.text(39.25, 6.2, "• Dose CaCO3, CaO, NaHCO3\n• Prevent soft-shell molting\n• Target alkalinity ≥120ppm\n• Stabilize diurnal swings",
            ha="center", va="center", fontsize=6.6, color="#334155", linespacing=1.2)

    # Pillar 3: Ammonia & Molasses
    draw_subcard(52.0, 3.6, 21.5, 7.2, "#ffffff", "#94a3b8")
    ax.text(62.75, 9.6, "Toxic NH3 Mitigation", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#0f172a")
    ax.text(62.75, 8.6, "Carbon:Nitrogen Control", ha="center", va="center", fontsize=7.0, color="#ea580c", fontweight="bold")
    ax.text(62.75, 6.2, "• Apply fermented molasses\n• Stimulate biofloc bacteria\n• Strip unionized NH3 gas\n• Prevent gill damage",
            ha="center", va="center", fontsize=6.6, color="#334155", linespacing=1.2)

    # Pillar 4: Feeding & Yield
    draw_subcard(75.5, 3.6, 21.5, 7.2, "#ffffff", "#94a3b8")
    ax.text(86.25, 9.6, "Feeding & Biomass", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#0f172a")
    ax.text(86.25, 8.6, "FCR & Growth Control", ha="center", va="center", fontsize=7.0, color="#7c3aed", fontweight="bold")
    ax.text(86.25, 6.2, "• Adjust tray feed rations\n• Suppress feed during stress\n• Add Vitamin C & probiotics\n• Maximize survival & ROI",
            ha="center", va="center", fontsize=6.6, color="#334155", linespacing=1.2)

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
    print(f"Diagram successfully built and saved to:\n  - {output_png.resolve()}\n  - {artifact_png.resolve()}")

if __name__ == "__main__":
    build_advanced_architecture_diagram()
