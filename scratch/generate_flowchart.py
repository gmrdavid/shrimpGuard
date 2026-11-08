import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon

def generate_hardware_to_system_flowchart():
    # Width 12.0 inches, Height 22.0 inches @ 200 DPI -> 2400 x 4400 px
    fig, ax = plt.subplots(figsize=(12.0, 22.0), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")

    BRAND_TEAL = "#126b4f"
    BRAND_DARK = "#093325"

    def draw_phase_bg(y, h, title, subtitle, bg_color, border_color):
        box = FancyBboxPatch(
            (4, y), 92, h,
            boxstyle="round,pad=0,rounding_size=1.0",
            facecolor=bg_color,
            edgecolor=border_color,
            linewidth=1.2,
            zorder=2
        )
        ax.add_patch(box)
        # Phase header tag
        ax.text(6.5, y + h - 1.6, title, fontsize=9.5, fontweight="bold", color=border_color, family="sans-serif")
        ax.text(6.5, y + h - 2.8, subtitle, fontsize=7.2, fontstyle="italic", color="#64748b", family="sans-serif")
        return box

    def draw_process_box(x, y, w, h, title, subtext, bg_color="#ffffff", border_color="#0284c7", zorder=3):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0,rounding_size=0.6",
            facecolor=bg_color,
            edgecolor=border_color,
            linewidth=1.2,
            zorder=zorder
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a", family="sans-serif")
        ax.text(x + w / 2, y + h * 0.32, subtext, ha="center", va="center", fontsize=6.8, color="#475569", family="sans-serif")
        return box

    def draw_decision_diamond(x, y, w, h, title, subtext, bg_color="#fef3c7", border_color="#d97706", zorder=3):
        pts = [
            [x + w / 2, y + h],      # top
            [x + w, y + h / 2],      # right
            [x + w / 2, y],          # bottom
            [x, y + h / 2]           # left
        ]
        poly = Polygon(pts, closed=True, facecolor=bg_color, edgecolor=border_color, linewidth=1.4, zorder=zorder)
        ax.add_patch(poly)
        ax.text(x + w / 2, y + h * 0.58, title, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#78350f", family="sans-serif")
        ax.text(x + w / 2, y + h * 0.38, subtext, ha="center", va="center", fontsize=6.5, color="#92400e", family="sans-serif")

    def draw_terminal(x, y, w, h, text, bg_color=BRAND_TEAL, text_color="#ffffff"):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0,rounding_size=1.5",
            facecolor=bg_color,
            edgecolor=BRAND_DARK,
            linewidth=1.5,
            zorder=4
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9.5, fontweight="bold", color=text_color, family="sans-serif")

    def draw_arrow(x1, y1, x2, y2, color="#475569", width=1.6, label=""):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color=color,
                lw=width,
                mutation_scale=13,
                shrinkA=0,
                shrinkB=0
            ),
            zorder=5
        )
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx + 1.2, my, label, fontsize=7.2, fontweight="bold", color=color, va="center")

    # =========================================================================
    # HEADER BANNER
    # =========================================================================
    header_box = FancyBboxPatch(
        (4, 96.2), 92, 3.0,
        boxstyle="round,pad=0,rounding_size=0.8",
        facecolor="#f0fdf4",
        edgecolor=BRAND_TEAL,
        linewidth=1.8,
        zorder=2
    )
    ax.add_patch(header_box)
    ax.text(50, 98.0, "SHRIMPGUARD: END-TO-END SYSTEM FLOWCHART",
            ha="center", va="center", fontsize=14, fontweight="bold", color=BRAND_DARK, family="sans-serif")
    ax.text(50, 96.9, "From Pond Water Quality Probes to LoRa Telemetry, ML/AI Intelligence, and Precision Farmer Actions",
            ha="center", va="center", fontsize=8.2, color="#334155", family="sans-serif")

    # START TERMINAL
    draw_terminal(38, 92.5, 24, 2.4, "START: POND MONITORING CYCLE")
    draw_arrow(50, 92.5, 50, 91.0)

    # =========================================================================
    # PHASE 1: POND SENSING & EDGE ACQUISITION (NODE 1)
    # Y-range: 79.5 to 91.0 (h = 11.5)
    # =========================================================================
    draw_phase_bg(79.5, 11.5, "PHASE 1: EDGE SENSING & INFERENCE (NODE 1 POND TRANSMITTER)",
                  "Submersible sensors read pond water and ESP32 executes on-chip Decision Tree classification",
                  "#f0f9ff", "#0284c7")

    # Two parallel sensors
    draw_process_box(10, 83.0, 36, 4.2, "DFRobot Analog pH Sensor",
                     "ADC1 GPIO 35 • 12-bit conversion & auto-temp compensation", "#ffffff", "#0284c7")
    draw_process_box(54, 83.0, 36, 4.2, "DS18B20 Temperature Sensor",
                     "GPIO 4 • 1-Wire Dallas bus • 12-bit non-blocking read", "#ffffff", "#0284c7")

    draw_arrow(50, 91.0, 28, 87.2)
    draw_arrow(50, 91.0, 72, 87.2)

    draw_arrow(28, 83.0, 42, 80.8)
    draw_arrow(72, 83.0, 58, 80.8)

    # ESP32 Node 1 Processing
    draw_process_box(20, 77.2, 60, 3.8, "ESP32 Node 1: Edge ML & Packet Encoding",
                     "Runs WaterQualityModel.h Decision Tree (Optimal/Warning/Critical) • Builds CSV Packet", "#ecfdf5", "#10b981")

    draw_arrow(50, 77.2, 50, 75.8)

    # =========================================================================
    # PHASE 2: WIRELESS LORA RF TELEMETRY TRANSMISSION
    # Y-range: 65.5 to 75.8 (h = 10.3)
    # =========================================================================
    draw_phase_bg(65.5, 10.3, "PHASE 2: LONG-RANGE LORA RF TRANSMISSION & RECEPTION",
                  "Sub-GHz wireless packet broadcast from pond across open water to base station",
                  "#fff7ed", "#ea580c")

    draw_process_box(8, 68.8, 38, 4.0, "SX1278 LoRa Transmitter (Node 1)",
                     "SPI (GPIO 5,18,19,23) • Ra-02 433.5 MHz ISM • Broadcasts packet", "#ffffff", "#ea580c")

    draw_process_box(54, 68.8, 38, 4.0, "SX1278 LoRa Receiver (Node 2 Gateway)",
                     "DIO0 IRQ • Packet capture, CRC & RSSI/SNR signal check", "#ffffff", "#ea580c")

    draw_arrow(50, 75.8, 27, 72.8)
    draw_arrow(46, 70.8, 54, 70.8, color="#ea580c", width=2.0, label="433.5 MHz LoRa")

    draw_arrow(73, 68.8, 50, 64.6)

    # =========================================================================
    # PHASE 3: NODE 2 LOCAL BASE STATION MONITORING & ALERTS
    # Y-range: 52.8 to 64.6 (h = 11.8)
    # =========================================================================
    draw_phase_bg(52.8, 11.8, "PHASE 3: BASE STATION LOCAL MONITORING & AUDIO-VISUAL SIGNALING",
                  "Immediate physical field feedback for pond workers via 20x4 LCD, Tricolor LEDs, and Buzzer",
                  "#f5f3ff", "#7c3aed")

    # Center: Node 2 local updates
    draw_process_box(15, 58.2, 70, 3.8, "Node 2 Base Station: Local UI & Audio-Visual Control",
                     "Displays Live Temp, pH, Status, RSSI on 20x4 I2C LCD • Drives LEDs & Piezo Buzzer", "#ffffff", "#7c3aed")

    # 3 sub-outputs
    draw_process_box(7, 53.6, 26, 3.6, "20x4 Character LCD", "Field live telemetry display", "#faf5ff", "#a855f7")
    draw_process_box(37, 53.6, 26, 3.6, "Tricolor Status LEDs", "Green (Opt) / Yellow / Red", "#faf5ff", "#a855f7")
    draw_process_box(67, 53.6, 26, 3.6, "Active Piezo Buzzer", "Silent / Slow Pulse / Rapid 5Hz", "#faf5ff", "#a855f7")

    draw_arrow(50, 58.2, 20, 57.2)
    draw_arrow(50, 58.2, 50, 57.2)
    draw_arrow(50, 58.2, 80, 57.2)

    # Serial stream to host
    draw_arrow(50, 53.6, 50, 51.6, label="USB CDC Serial @ 115200")

    # =========================================================================
    # PHASE 4: INGESTION, DATABASE & ML/AI INTELLIGENCE (FLASK BACKEND)
    # Y-range: 35.0 to 51.6 (h = 16.6)
    # =========================================================================
    draw_phase_bg(35.0, 16.6, "PHASE 4: SHRIMPGUARD SERVER INGESTION, STORAGE & AI ADVISORY",
                  "Win32 serial listener forwards telemetry to Flask REST API, MySQL database, and AI engine",
                  "#ecfdf5", "#059669")

    draw_process_box(20, 46.8, 60, 3.6, "Win32 Hardware Serial Listener -> POST /api/readings",
                     "hardware_serial.py auto-detects COM port & posts reading with API key authentication", "#ffffff", "#059669")

    draw_arrow(50, 51.6, 50, 50.4)
    draw_arrow(50, 46.8, 50, 45.4)

    draw_process_box(10, 41.5, 36, 3.8, "MySQL Relational Database",
                     "Inserts record into 'sensors' table • Logs activity", "#f0fdf4", "#10b981")
    draw_process_box(54, 41.5, 36, 3.8, "Scikit-Learn ML Model Validation",
                     "best_water_quality_model.joblib evaluates thresholds", "#f0fdf4", "#10b981")

    draw_arrow(50, 45.4, 28, 45.3)
    draw_arrow(50, 45.4, 72, 45.3)

    # Decision diamond
    draw_decision_diamond(35, 35.8, 30, 4.6, "Status Warning or Critical?",
                          "ML classification check", "#fef3c7", "#d97706")

    draw_arrow(28, 41.5, 42, 40.4)
    draw_arrow(72, 41.5, 58, 40.4)

    # Decision branches
    # YES -> Left to Gemini AI & ntfy.sh
    # NO  -> Right to Nominal Log
    draw_arrow(35, 38.1, 16, 38.1, color="#dc2626", width=1.8, label="YES (Abnormal)")
    draw_arrow(65, 38.1, 84, 38.1, color="#16a34a", width=1.8, label="NO (Optimal)")

    # =========================================================================
    # PHASE 5: MULTI-TIER ALERTING & PUSH NOTIFICATIONS
    # Y-range: 22.0 to 34.2 (h = 12.2)
    # =========================================================================
    draw_phase_bg(22.0, 12.2, "PHASE 5: MULTI-CHANNEL ALERTS & CLOUD NOTIFICATIONS",
                  "Automated trigger of Google Gemini AI biological advice, ntfy.sh mobile push, and dashboard alerts",
                  "#eef2ff", "#4f46e5")

    # Left: Emergency Flow (Gemini + ntfy.sh)
    draw_process_box(6, 27.2, 40, 4.0, "Google Gemini AI Decision Engine",
                     "Generates Penaeus vannamei diagnoses, liming & aeration steps", "#faf5ff", "#9333ea")
    draw_process_box(6, 22.6, 40, 3.8, "ntfy.sh Mobile Cloud Push Service",
                     "Dispatches urgent push alert to farmer's phone & browser", "#e0e7ff", "#4338ca")

    draw_arrow(16, 38.1, 16, 31.2)
    draw_arrow(26, 27.2, 26, 26.4)

    # Right: Nominal Log
    draw_process_box(54, 25.2, 40, 4.2, "Nominal Status Logged & Standby",
                     "Pond water within optimal bounds (28–32°C, pH 7.5–8.5)\nTelemetry stored for trend analysis", "#f0fdf4", "#16a34a")
    draw_arrow(84, 38.1, 84, 29.4)

    # Both lead to Web Dashboard
    draw_arrow(26, 22.6, 38, 20.2)
    draw_arrow(74, 25.2, 62, 20.2)

    # =========================================================================
    # PHASE 6: SHRIMPGUARD WEB DASHBOARD & USER ACTIONS
    # Y-range: 7.2 to 20.2 (h = 13.0)
    # =========================================================================
    draw_phase_bg(7.2, 13.0, "PHASE 6: WEB DASHBOARD VISUALIZATION & USER DECISION MAKING",
                  "Real-time gauges, historical calendar filter, calculators, and precision farming interventions",
                  "#f0fdfa", "#0d9488")

    draw_process_box(15, 14.8, 70, 3.8, "ShrimpGuard Responsive Web Dashboard",
                     "Live Telemetry Dials • Historical Calendar Filter (Green/Red) • Tools & Calculators • Devices Inventory",
                     "#ffffff", "#0d9488")

    # 4 Precision Actions
    draw_process_box(6, 8.2, 20.5, 4.8, "Aeration Control", "Modulate paddlewheels\nMaintain DO > 5.0 mg/L", "#f8fafc", "#0284c7")
    draw_process_box(28.5, 8.2, 20.5, 4.8, "pH & Liming Dosing", "Dose CaCO3 / NaHCO3\nPrevent soft molting", "#f8fafc", "#16a34a")
    draw_process_box(51.0, 8.2, 20.5, 4.8, "Toxic NH3 Mitigation", "Dose fermented molasses\nC:N biofloc balance", "#f8fafc", "#ea580c")
    draw_process_box(73.5, 8.2, 20.5, 4.8, "Feed Adjustments", "Optimize feeding trays\nPrevent organic pollution", "#f8fafc", "#7c3aed")

    draw_arrow(50, 14.8, 16.25, 13.0)
    draw_arrow(50, 14.8, 38.75, 13.0)
    draw_arrow(50, 14.8, 61.25, 13.0)
    draw_arrow(50, 14.8, 83.75, 13.0)

    # Loop back arrow from actions to next cycle
    ax.annotate(
        "",
        xy=(94, 93.7),
        xytext=(94, 10.6),
        arrowprops=dict(
            arrowstyle="-|>",
            color="#64748b",
            lw=1.5,
            linestyle="dashed",
            mutation_scale=12,
            shrinkA=0,
            shrinkB=0
        ),
        zorder=5
    )
    ax.text(95.2, 50.0, "Continuous 5-Second Telemetry Monitoring Cycle",
            rotation=270, va="center", ha="left", fontsize=7.2, color="#64748b", fontweight="semibold")

    # END TERMINAL
    draw_terminal(38, 2.8, 24, 2.4, "END / CONTINUOUS LOOP")
    draw_arrow(50, 8.2, 50, 5.2)

    # Caption
    ax.text(50, 0.8, "Figure 4. End-to-End System Flowchart: Hardware Sensors to ShrimpGuard Web Application",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color="#0f172a", family="sans-serif")

    # Save PNG and JPG
    output_png = Path("static/images/hardware_to_shrimpguard_flowchart.png")
    output_jpg = Path("static/images/hardware_to_shrimpguard_flowchart.jpg")
    artifact_png = Path(r"C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188\hardware_to_shrimpguard_flowchart.png")
    artifact_jpg = Path(r"C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188\hardware_to_shrimpguard_flowchart.jpg")

    plt.tight_layout(pad=0.2)
    fig.savefig(output_png, format="png", dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    fig.savefig(artifact_png, format="png", dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    from PIL import Image
    img_conv = Image.open(output_png).convert("RGB")
    img_conv.save(output_jpg, format="JPEG", quality=95)
    img_conv.save(artifact_jpg, format="JPEG", quality=95)

    print("Hardware to ShrimpGuard flowchart generated successfully!")
    print(f"  - PNG: {output_png.resolve()} ({output_png.stat().st_size} bytes)")
    print(f"  - JPG: {output_jpg.resolve()} ({output_jpg.stat().st_size} bytes)")

if __name__ == "__main__":
    generate_hardware_to_system_flowchart()
