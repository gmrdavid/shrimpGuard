import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from PIL import Image

def build_simplified_architecture_diagram():
    # Aspect ratio similar to original: ~1:1.75
    # Width: 10 inches, Height: 17.5 inches @ 200 DPI -> 2000 x 3500 px
    fig, ax = plt.subplots(figsize=(10.0, 17.5), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    def draw_layer_card(y, h, bg_color, border_color):
        box = FancyBboxPatch(
            (4, y), 92, h,
            boxstyle="round,pad=0,rounding_size=1.2",
            facecolor=bg_color,
            edgecolor=border_color,
            linewidth=1.5,
            zorder=2
        )
        ax.add_patch(box)
        return box

    def draw_item_card(x, y, w, h, bg_color="#ffffff", border_color="#e2e8f0"):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0,rounding_size=0.8",
            facecolor=bg_color,
            edgecolor=border_color,
            linewidth=1.0,
            zorder=3
        )
        ax.add_patch(box)
        return box

    def draw_arrow(x, y_start, y_end, color="#64748b", width=2.0):
        ax.annotate(
            "",
            xy=(x, y_end),
            xytext=(x, y_start),
            arrowprops=dict(
                arrowstyle="-|>",
                color=color,
                lw=width,
                mutation_scale=15,
                shrinkA=0,
                shrinkB=0
            ),
            zorder=5
        )

    def draw_h_arrow(x_start, x_end, y, color="#64748b", width=1.5):
        ax.annotate(
            "",
            xy=(x_end, y),
            xytext=(x_start, y),
            arrowprops=dict(
                arrowstyle="-|>",
                color=color,
                lw=width,
                mutation_scale=12,
                shrinkA=0,
                shrinkB=0
            ),
            zorder=5
        )

    def draw_double_arrow(x1, y1, x2, y2, color="#64748b", width=1.5):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="<->",
                color=color,
                lw=width,
                mutation_scale=12,
                shrinkA=0,
                shrinkB=0
            ),
            zorder=5
        )

    def embed_crop(name, x, y, w, h, zorder=4):
        crop_path = Path(f"scratch/crops/{name}.png")
        if crop_path.exists():
            img = Image.open(crop_path)
            ax.imshow(img, extent=(x, x + w, y, y + h), aspect="auto", zorder=zorder)

    # =========================================================================
    # 1. IOT SENSING LAYER (Light Blue)
    # Y-range: 87.0 to 98.2 (h = 11.2)
    # =========================================================================
    draw_layer_card(87.0, 11.2, "#e0f2fe", "#7dd3fc")
    ax.text(50, 96.6, "1. IOT SENSING LAYER", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#0369a1", family="sans-serif")
    ax.text(50, 95.2, "Water Quality Sensors", ha="center", va="center",
            fontsize=9.0, color="#0284c7", family="sans-serif")

    # 3 Probes: pH, Temperature, Expansion
    # Item 1: pH Sensor
    draw_item_card(9, 88.0, 24, 6.2, "#ffffff", "#bae6fd")
    embed_crop("ph_sensor", 18.5, 90.0, 5.0, 3.8)
    ax.text(21, 89.2, "pH Sensor", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax.text(21, 88.4, "(DFRobot Gravity SEN0161)", ha="center", va="center", fontsize=6.8, color="#64748b")

    # Item 2: Temperature Sensor
    draw_item_card(38, 88.0, 24, 6.2, "#ffffff", "#bae6fd")
    embed_crop("temp_sensor", 47.0, 90.0, 6.0, 3.8)
    ax.text(50, 89.2, "Temperature Sensor", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax.text(50, 88.4, "(DS18B20 Waterproof 1-Wire)", ha="center", va="center", fontsize=6.8, color="#64748b")

    # Item 3: Bio-Parameters
    draw_item_card(67, 88.0, 24, 6.2, "#ffffff", "#bae6fd")
    embed_crop("cloud_db", 76.5, 90.0, 5.0, 3.8)
    ax.text(79, 89.2, "Bio-Parameters", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax.text(79, 88.4, "(Toxic NH3, CO2, Salinity)", ha="center", va="center", fontsize=6.8, color="#64748b")

    draw_arrow(50, 87.0, 85.6)

    # =========================================================================
    # 2. DEVICE PROCESSING AND LOCAL MONITORING (Mint Green)
    # Y-range: 71.0 to 85.6 (h = 14.6)
    # =========================================================================
    draw_layer_card(71.0, 14.6, "#dcfce7", "#86efac")
    ax.text(50, 84.1, "2. DEVICE PROCESSING & EDGE INTELLIGENCE", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#15803d", family="sans-serif")
    ax.text(50, 82.8, "ESP32 (Node 1) collects, processes, executes on-chip ML, and broadcasts telemetry", ha="center", va="center",
            fontsize=8.5, color="#16a34a", family="sans-serif")

    # Left Column: Embedded ML + Solar Power
    draw_item_card(7, 77.2, 26, 4.8, "#ffffff", "#bbf7d0")
    embed_crop("ml_brain", 8.5, 77.6, 4.0, 4.0)
    ax.text(21, 79.9, "Embedded Edge ML", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#0f172a")
    ax.text(21, 78.5, "(On-Chip Decision Tree)", ha="center", va="center", fontsize=6.8, color="#64748b")

    draw_item_card(7, 71.8, 26, 4.8, "#ffffff", "#bbf7d0")
    embed_crop("lora_gateway", 8.5, 72.2, 4.0, 4.0)
    ax.text(21, 74.5, "Solar & Battery Power", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#0f172a")
    ax.text(21, 73.1, "(3.7V Li-ion + Solar MPPT)", ha="center", va="center", fontsize=6.8, color="#64748b")

    # Center: ESP32 Node 1
    draw_item_card(38, 72.0, 24, 9.8, "#ffffff", "#4ade80")
    embed_crop("esp32", 46.5, 75.0, 7.0, 6.2)
    ax.text(50, 74.0, "ESP32 Node 1", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0f172a")
    ax.text(50, 72.8, "(Autonomous Pond Transmitter)", ha="center", va="center", fontsize=6.8, color="#16a34a", fontweight="bold")

    # Right Column: SX1278 LoRa Module
    draw_item_card(67, 74.5, 26, 5.0, "#ffffff", "#bbf7d0")
    embed_crop("lora_module", 68.5, 74.9, 4.2, 4.2)
    ax.text(81, 77.3, "LoRa Module (SX1278)", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#0f172a")
    ax.text(81, 75.9, "(433.5 MHz Transceiver)", ha="center", va="center", fontsize=6.8, color="#64748b")

    # Connectors inside Layer 2
    draw_double_arrow(33, 79.6, 38, 77.0, color="#16a34a")
    draw_double_arrow(33, 74.2, 38, 76.0, color="#16a34a")
    draw_double_arrow(62, 77.0, 67, 77.0, color="#16a34a")

    draw_arrow(50, 71.0, 69.6)

    # =========================================================================
    # 3. COMMUNICATION LAYER (Peach / Orange)
    # Y-range: 58.2 to 69.6 (h = 11.4)
    # =========================================================================
    draw_layer_card(58.2, 11.4, "#ffedd5", "#fed7aa")
    ax.text(50, 68.2, "3. COMMUNICATION LAYER", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#c2410c", family="sans-serif")
    ax.text(50, 66.9, "Long-range Sub-GHz LoRa RF data transmission from pond to base station", ha="center", va="center",
            fontsize=8.5, color="#ea580c", family="sans-serif")

    # Left: Node 1 LoRa TX
    draw_item_card(8, 59.2, 26, 6.4, "#ffffff", "#fdba74")
    embed_crop("lora_module", 18.5, 61.8, 5.0, 3.5)
    ax.text(21, 60.8, "LoRa Module (SX1278)", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#0f172a")
    ax.text(21, 59.8, "(Pond Node 1 Transmitter)", ha="center", va="center", fontsize=6.8, color="#64748b")

    # Center: Long Range Wireless transmission
    embed_crop("lora_antenna", 46.5, 62.0, 7.0, 4.0)
    ax.text(50, 60.8, "Long-Range LoRa RF", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#c2410c")
    ax.text(50, 59.8, "(433.5 MHz Chirp Spread Spectrum)", ha="center", va="center", fontsize=6.5, color="#ea580c")
    draw_h_arrow(34.5, 45.5, 63.8, color="#f97316", width=2.0)
    draw_h_arrow(54.5, 65.5, 63.8, color="#f97316", width=2.0)

    # Right: Node 2 Gateway & Receiver
    draw_item_card(66, 59.2, 26, 6.4, "#ffffff", "#fdba74")
    embed_crop("lora_gateway", 76.5, 61.8, 5.0, 3.5)
    ax.text(79, 60.8, "LoRa Receiver Gateway", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#0f172a")
    ax.text(79, 59.8, "(Node 2 ESP32 Base Station)", ha="center", va="center", fontsize=6.8, color="#64748b")

    draw_arrow(50, 58.2, 56.8)

    # =========================================================================
    # 4. CLOUD INTELLIGENCE LAYER (Lavender / Purple)
    # Y-range: 44.8 to 56.8 (h = 12.0)
    # =========================================================================
    draw_layer_card(44.8, 12.0, "#f3e8ff", "#e9d5ff")
    ax.text(50, 55.4, "4. CLOUD INTELLIGENCE LAYER", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#7e22ce", family="sans-serif")
    ax.text(50, 54.1, "Flask backend server, MySQL relational storage, ML validation & Gemini AI advisory", ha="center", va="center",
            fontsize=8.5, color="#9333ea", family="sans-serif")

    # Item 1: Cloud Database
    draw_item_card(8, 45.8, 25, 7.0, "#ffffff", "#d8b4fe")
    embed_crop("cloud_db", 18.0, 48.8, 5.0, 3.6)
    ax.text(20.5, 47.7, "Cloud Database", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax.text(20.5, 46.7, "(Flask & MySQL Storage)", ha="center", va="center", fontsize=6.8, color="#64748b")

    # Arrow 1 -> 2
    draw_h_arrow(33.5, 37.0, 49.3, color="#a855f7", width=2.0)

    # Item 2: Machine Learning Model
    draw_item_card(37.5, 45.8, 25, 7.0, "#ffffff", "#d8b4fe")
    embed_crop("ml_brain", 47.5, 48.8, 5.0, 3.6)
    ax.text(50, 47.7, "Machine Learning Model", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax.text(50, 46.7, "(Optimal / Warning / Critical)", ha="center", va="center", fontsize=6.8, color="#64748b")

    # Arrow 2 -> 3
    draw_h_arrow(63.0, 66.5, 49.3, color="#a855f7", width=2.0)

    # Item 3: AI-Based Decision Support
    draw_item_card(67, 45.8, 25, 7.0, "#ffffff", "#d8b4fe")
    embed_crop("ai_head", 77.0, 48.8, 5.0, 3.6)
    ax.text(79.5, 47.7, "AI Decision Support", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax.text(79.5, 46.7, "(Google Gemini AI Advisory)", ha="center", va="center", fontsize=6.8, color="#64748b")

    draw_arrow(50, 44.8, 43.4)

    # =========================================================================
    # 5. ALERTS AND NOTIFICATIONS (Soft Blue)
    # Y-range: 30.8 to 43.4 (h = 12.6)
    # =========================================================================
    draw_layer_card(30.8, 12.6, "#e0e7ff", "#c7d2fe")
    ax.text(50, 42.0, "5. ALERTS AND NOTIFICATIONS", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#3730a3", family="sans-serif")
    ax.text(50, 40.7, "Local on-site signaling, mobile cloud push, and real-time dashboard notifications", ha="center", va="center",
            fontsize=8.5, color="#4f46e5", family="sans-serif")

    # 4 Alert Cards:
    # 1. LED Indicators
    draw_item_card(6.5, 31.8, 20.5, 7.4, "#ffffff", "#a5b4fc")
    embed_crop("leds", 14.5, 35.0, 4.5, 3.8)
    ax.text(16.75, 33.8, "LED Indicators", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#0f172a")
    ax.text(16.75, 32.8, "(Green/Yellow/Red)", ha="center", va="center", fontsize=6.5, color="#64748b")

    # 2. Buzzer
    draw_item_card(28.5, 31.8, 20.5, 7.4, "#ffffff", "#a5b4fc")
    embed_crop("buzzer", 36.5, 35.0, 4.5, 3.8)
    ax.text(38.75, 33.8, "Active Buzzer", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#0f172a")
    ax.text(38.75, 32.8, "(Audible Multi-Cadence)", ha="center", va="center", fontsize=6.5, color="#64748b")

    # 3. Mobile Push (ntfy.sh)
    draw_item_card(50.5, 31.8, 20.5, 7.4, "#ffffff", "#a5b4fc")
    embed_crop("ntfy_phone", 58.5, 35.0, 4.5, 3.8)
    ax.text(60.75, 33.8, "Mobile Push", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#0f172a")
    ax.text(60.75, 32.8, "(ntfy.sh Instant Alert)", ha="center", va="center", fontsize=6.5, color="#64748b")

    # 4. System Alerts
    draw_item_card(72.5, 31.8, 20.5, 7.4, "#ffffff", "#a5b4fc")
    embed_crop("system_alert_bell", 80.5, 35.0, 4.5, 3.8)
    ax.text(82.75, 33.8, "System Alerts", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#0f172a")
    ax.text(82.75, 32.8, "(Web Dashboard)", ha="center", va="center", fontsize=6.5, color="#64748b")

    draw_arrow(50, 30.8, 29.4)

    # =========================================================================
    # 6. USER INTERFACE LAYER (Cyan / Aqua)
    # Y-range: 16.2 to 29.4 (h = 13.2)
    # =========================================================================
    draw_layer_card(16.2, 13.2, "#ccfbf1", "#99f6e4")
    ax.text(50, 28.0, "6. USER INTERFACE LAYER", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#0f766e", family="sans-serif")
    ax.text(50, 26.7, "ShrimpGuard Responsive Web-based Management Dashboard", ha="center", va="center",
            fontsize=8.5, color="#0d9488", family="sans-serif")

    # 4 UI Modules:
    # 1. Real-Time Monitoring
    draw_item_card(6.5, 17.2, 20.5, 8.0, "#ffffff", "#5eead4")
    embed_crop("ui_realtime", 14.5, 21.0, 4.5, 3.8)
    ax.text(16.75, 19.8, "Real-Time Monitoring", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0f172a")
    ax.text(16.75, 18.6, "(Live Gauges & Trends)", ha="center", va="center", fontsize=6.5, color="#64748b")

    # 2. Historical Trends
    draw_item_card(28.5, 17.2, 20.5, 8.0, "#ffffff", "#5eead4")
    embed_crop("ui_history", 36.5, 21.0, 4.5, 3.8)
    ax.text(38.75, 19.8, "Historical Trends", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0f172a")
    ax.text(38.75, 18.6, "(Calendar & Indicator)", ha="center", va="center", fontsize=6.5, color="#64748b")

    # 3. ML & Calculators
    draw_item_card(50.5, 17.2, 20.5, 8.0, "#ffffff", "#5eead4")
    embed_crop("ui_ml", 58.5, 21.0, 4.5, 3.8)
    ax.text(60.75, 19.8, "Aquaculture Tools", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0f172a")
    ax.text(60.75, 18.6, "(Calculators & Models)", ha="center", va="center", fontsize=6.5, color="#64748b")

    # 4. Devices & Hardware
    draw_item_card(72.5, 17.2, 20.5, 8.0, "#ffffff", "#5eead4")
    embed_crop("ui_alerts", 80.5, 21.0, 4.5, 3.8)
    ax.text(82.75, 19.8, "Devices & Hardware", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0f172a")
    ax.text(82.75, 18.6, "(Hardware Diagnostics)", ha="center", va="center", fontsize=6.5, color="#64748b")

    draw_arrow(50, 16.2, 14.8)

    # =========================================================================
    # 7. USER DECISION MAKING (Neutral Gray)
    # Y-range: 4.8 to 14.8 (h = 10.0)
    # =========================================================================
    draw_layer_card(4.8, 10.0, "#f1f5f9", "#cbd5e1")
    ax.text(50, 13.4, "7. USER DECISION MAKING", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#1e293b", family="sans-serif")
    ax.text(50, 12.1, "Enables farmers to take timely and informed actions for better aquaculture management", ha="center", va="center",
            fontsize=8.5, color="#475569", family="sans-serif")

    # 4 Action Pills:
    draw_item_card(6.5, 5.8, 20.5, 5.0, "#ffffff", "#94a3b8")
    ax.text(16.75, 8.8, "Aeration Control", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0284c7")
    ax.text(16.75, 7.3, "(DO > 5.0 mg/L & Thermal Mix)", ha="center", va="center", fontsize=6.2, color="#475569")

    draw_item_card(28.5, 5.8, 20.5, 5.0, "#ffffff", "#94a3b8")
    ax.text(38.75, 8.8, "pH & Liming", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#16a34a")
    ax.text(38.75, 7.3, "(CaCO3 & Buffer Dosing)", ha="center", va="center", fontsize=6.2, color="#475569")

    draw_item_card(50.5, 5.8, 20.5, 5.0, "#ffffff", "#94a3b8")
    ax.text(60.75, 8.8, "Ammonia Remediation", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#ea580c")
    ax.text(60.75, 7.3, "(Molasses / Biofloc C:N)", ha="center", va="center", fontsize=6.2, color="#475569")

    draw_item_card(72.5, 5.8, 20.5, 5.0, "#ffffff", "#94a3b8")
    ax.text(82.75, 8.8, "Feed Management", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#7c3aed")
    ax.text(82.75, 7.3, "(Tray Rations & Survival)", ha="center", va="center", fontsize=6.2, color="#475569")

    # =========================================================================
    # CAPTION AT BOTTOM
    # =========================================================================
    ax.text(50, 2.0, "Figure 3. System Architectural Design", ha="center", va="center",
            fontsize=12.0, fontweight="bold", color="#0f172a", family="sans-serif")

    # Save to both locations
    output_png = Path("static/images/system_architecture_diagram.png")
    output_jpg = Path("static/images/system_architecture_diagram.jpg")
    artifact_png = Path(r"C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188\system_architecture_diagram.png")
    artifact_jpg = Path(r"C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188\system_architecture_diagram.jpg")

    plt.tight_layout(pad=0.2)
    fig.savefig(output_png, format="png", dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    fig.savefig(artifact_png, format="png", dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    # Convert to JPEG as well
    img_conv = Image.open(output_png).convert("RGB")
    img_conv.save(output_jpg, format="JPEG", quality=95)
    img_conv.save(artifact_jpg, format="JPEG", quality=95)

    print("Simplified architecture diagram successfully generated!")
    print(f"  - PNG: {output_png.resolve()} ({output_png.stat().st_size} bytes)")
    print(f"  - JPG: {output_jpg.resolve()} ({output_jpg.stat().st_size} bytes)")

if __name__ == "__main__":
    build_simplified_architecture_diagram()
