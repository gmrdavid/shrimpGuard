import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from PIL import Image

def generate_perfect_simplified_diagram():
    # Size: 10 x 17.5 inches @ 220 DPI -> 2200 x 3850 px (matching user's original ~1:1.7 aspect ratio)
    fig, ax = plt.subplots(figsize=(10.0, 17.5), dpi=220)
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
            linewidth=1.4,
            zorder=2
        )
        ax.add_patch(box)
        return box

    def draw_subcard(x, y, w, h, bg_color="#ffffff", border_color="#e2e8f0"):
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

    def draw_v_arrow(x, y_start, y_end, color="#64748b", width=2.0):
        ax.annotate(
            "",
            xy=(x, y_end),
            xytext=(x, y_start),
            arrowprops=dict(
                arrowstyle="-|>",
                color=color,
                lw=width,
                mutation_scale=14,
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
    # 1. IOT SENSING LAYER (Light Sky Blue: #e0f2fe)
    # =========================================================================
    draw_layer_card(86.5, 11.5, "#e0f2fe", "#7dd3fc")
    ax.text(50, 96.6, "1. IOT SENSING LAYER", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#0369a1", family="sans-serif")
    ax.text(50, 95.3, "Water Quality Sensors", ha="center", va="center",
            fontsize=9.0, color="#0284c7", family="sans-serif")

    # Item 1: pH Sensor
    draw_subcard(7, 87.5, 26, 6.6, "#ffffff", "#bae6fd")
    embed_crop("ph_sensor", 17.5, 89.8, 5.0, 4.0)
    ax.text(20, 89.0, "pH Sensor", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax.text(20, 88.1, "(DFRobot Gravity SEN0161)", ha="center", va="center", fontsize=6.8, color="#64748b")

    # Item 2: Temperature Sensor
    draw_subcard(37, 87.5, 26, 6.6, "#ffffff", "#bae6fd")
    embed_crop("temp_sensor", 47.0, 89.8, 6.0, 4.0)
    ax.text(50, 89.0, "Temperature Sensor", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax.text(50, 88.1, "(DS18B20 Waterproof 1-Wire)", ha="center", va="center", fontsize=6.8, color="#64748b")

    # Item 3: Bio-Parameters
    draw_subcard(67, 87.5, 26, 6.6, "#ffffff", "#bae6fd")
    embed_crop("cloud_db", 77.5, 89.8, 5.0, 4.0)
    ax.text(80, 89.0, "Bio-Parameters", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax.text(80, 88.1, "(Toxic NH3, CO2, Salinity)", ha="center", va="center", fontsize=6.8, color="#64748b")

    draw_v_arrow(50, 86.5, 85.0)

    # =========================================================================
    # 2. DEVICE PROCESSING AND LOCAL MONITORING (Mint Green: #dcfce7)
    # =========================================================================
    draw_layer_card(70.2, 14.8, "#dcfce7", "#86efac")
    ax.text(50, 83.5, "2. DEVICE PROCESSING AND LOCAL MONITORING", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#15803d", family="sans-serif")
    ax.text(50, 82.2, "ESP32 collects, processes, executes on-chip ML, stores, and manages alerts", ha="center", va="center",
            fontsize=8.5, color="#16a34a", family="sans-serif")

    # Left: 20x4 LCD + Embedded Edge ML
    draw_subcard(7, 76.5, 27, 4.6, "#ffffff", "#bbf7d0")
    embed_crop("lcd", 8.5, 77.0, 5.5, 3.6)
    ax.text(22, 79.3, "LCD Display", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#0f172a")
    ax.text(22, 77.9, "(20x4 I2C Telemetry)", ha="center", va="center", fontsize=6.8, color="#64748b")

    draw_subcard(7, 71.0, 27, 4.6, "#ffffff", "#bbf7d0")
    embed_crop("ml_brain", 9.0, 71.4, 4.5, 3.8)
    ax.text(22, 73.8, "Embedded Edge ML", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#0f172a")
    ax.text(22, 72.4, "(On-Chip Decision Tree)", ha="center", va="center", fontsize=6.8, color="#64748b")

    # Center: ESP32 Microcontroller
    draw_subcard(38.5, 71.0, 23, 10.1, "#ffffff", "#4ade80")
    embed_crop("esp32", 46.5, 74.4, 7.0, 6.2)
    ax.text(50, 73.2, "ESP32 Controller", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#0f172a")
    ax.text(50, 72.0, "(Dual-Core 240MHz)", ha="center", va="center", fontsize=6.8, color="#15803d", fontweight="bold")

    # Right: LEDs + Buzzer + Solar Power
    draw_subcard(66, 76.8, 27, 4.3, "#ffffff", "#bbf7d0")
    embed_crop("leds", 67.5, 77.2, 2.8, 3.5)
    ax.text(81, 79.4, "LED Indicators", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#0f172a")
    ax.text(81, 78.0, "(Green / Yellow / Red)", ha="center", va="center", fontsize=6.6, color="#64748b")

    draw_subcard(66, 71.0, 27, 5.0, "#ffffff", "#bbf7d0")
    embed_crop("buzzer", 67.5, 71.8, 3.8, 3.4)
    ax.text(81, 74.0, "Active Buzzer", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#0f172a")
    ax.text(81, 72.6, "(Audible Multi-Cadence)", ha="center", va="center", fontsize=6.6, color="#64748b")

    # Double arrows connecting ESP32 to peripheral blocks
    draw_double_arrow(34, 78.8, 38.5, 77.0, color="#16a34a")
    draw_double_arrow(34, 73.3, 38.5, 75.0, color="#16a34a")
    draw_double_arrow(61.5, 77.0, 66, 78.5, color="#16a34a")
    draw_double_arrow(61.5, 75.0, 66, 73.5, color="#16a34a")

    draw_v_arrow(50, 70.2, 68.8)

    # =========================================================================
    # 3. COMMUNICATION LAYER (Warm Peach: #ffedd5)
    # =========================================================================
    draw_layer_card(57.5, 11.3, "#ffedd5", "#fed7aa")
    ax.text(50, 67.4, "3. COMMUNICATION LAYER", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#c2410c", family="sans-serif")
    ax.text(50, 66.1, "Long-range Sub-GHz LoRa data transmission from pond to base station", ha="center", va="center",
            fontsize=8.5, color="#ea580c", family="sans-serif")

    # Left: LoRa Module SX1278
    draw_subcard(7, 58.5, 26, 6.4, "#ffffff", "#fdba74")
    embed_crop("lora_module", 17.5, 61.2, 5.0, 3.4)
    ax.text(20, 60.1, "LoRa Module (SX1278)", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#0f172a")
    ax.text(20, 59.1, "(Node 1 Transmitter)", ha="center", va="center", fontsize=6.8, color="#64748b")

    # Center: Long Range Transmission
    embed_crop("lora_antenna", 46.5, 61.5, 7.0, 3.8)
    ax.text(50, 60.1, "Long-Range LoRa RF", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#c2410c")
    ax.text(50, 59.1, "(433.5 MHz Telemetry Link)", ha="center", va="center", fontsize=6.6, color="#ea580c")
    draw_h_arrow(33.5, 45.5, 63.2, color="#f97316", width=2.0)
    draw_h_arrow(54.5, 66.5, 63.2, color="#f97316", width=2.0)

    # Right: LoRa Base Station Gateway
    draw_subcard(67, 58.5, 26, 6.4, "#ffffff", "#fdba74")
    embed_crop("lora_gateway", 77.5, 61.2, 5.0, 3.4)
    ax.text(80, 60.1, "LoRa Base Gateway", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#0f172a")
    ax.text(80, 59.1, "(Node 2 USB Serial Bridge)", ha="center", va="center", fontsize=6.8, color="#64748b")

    draw_v_arrow(50, 57.5, 56.0)

    # =========================================================================
    # 4. CLOUD INTELLIGENCE LAYER (Lavender / Purple: #f3e8ff)
    # =========================================================================
    draw_layer_card(44.2, 11.8, "#f3e8ff", "#e9d5ff")
    ax.text(50, 54.6, "4. CLOUD INTELLIGENCE LAYER", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#7e22ce", family="sans-serif")
    ax.text(50, 53.3, "Flask backend server, MySQL relational storage, ML validation & Gemini AI advisory", ha="center", va="center",
            fontsize=8.5, color="#9333ea", family="sans-serif")

    # 3 Cards: Cloud Database -> Machine Learning Model -> AI Decision Support
    draw_subcard(7, 45.2, 26, 6.8, "#ffffff", "#d8b4fe")
    embed_crop("cloud_db", 17.5, 48.0, 5.0, 3.6)
    ax.text(20, 47.0, "Cloud Database", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax.text(20, 46.0, "(Real-time & Historical Data)", ha="center", va="center", fontsize=6.8, color="#64748b")

    draw_h_arrow(33.5, 36.5, 48.6, color="#a855f7", width=2.0)

    draw_subcard(37, 45.2, 26, 6.8, "#ffffff", "#d8b4fe")
    embed_crop("ml_brain", 47.5, 48.0, 5.0, 3.6)
    ax.text(50, 47.0, "Machine Learning Model", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax.text(50, 46.0, "(Optimal / Warning / Critical)", ha="center", va="center", fontsize=6.8, color="#64748b")

    draw_h_arrow(63.5, 66.5, 48.6, color="#a855f7", width=2.0)

    draw_subcard(67, 45.2, 26, 6.8, "#ffffff", "#d8b4fe")
    embed_crop("ai_head", 77.5, 48.0, 5.0, 3.6)
    ax.text(80, 47.0, "AI Decision Support", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#0f172a")
    ax.text(80, 46.0, "(Google Gemini AI Advisory)", ha="center", va="center", fontsize=6.8, color="#64748b")

    draw_v_arrow(50, 44.2, 42.8)

    # =========================================================================
    # 5. ALERTS AND NOTIFICATIONS (Soft Indigo / Blue: #e0e7ff)
    # =========================================================================
    draw_layer_card(30.6, 12.2, "#e0e7ff", "#c7d2fe")
    ax.text(50, 41.4, "5. ALERTS AND NOTIFICATIONS", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#3730a3", family="sans-serif")
    ax.text(50, 40.2, "Local visual & audible alarms, mobile cloud push, and dashboard alerts", ha="center", va="center",
            fontsize=8.5, color="#4f46e5", family="sans-serif")

    # 4 Alert Cards: LEDs, Buzzer, Mobile Push, System Alerts
    draw_subcard(6, 31.6, 20.5, 7.2, "#ffffff", "#a5b4fc")
    embed_crop("leds", 14.2, 34.6, 4.0, 3.8)
    ax.text(16.25, 33.6, "LED Indicators", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#0f172a")
    ax.text(16.25, 32.6, "(Local Visual Alert)", ha="center", va="center", fontsize=6.5, color="#64748b")

    draw_subcard(28.5, 31.6, 20.5, 7.2, "#ffffff", "#a5b4fc")
    embed_crop("buzzer", 36.7, 34.6, 4.0, 3.8)
    ax.text(38.75, 33.6, "Active Buzzer", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#0f172a")
    ax.text(38.75, 32.6, "(Audible Alert)", ha="center", va="center", fontsize=6.5, color="#64748b")

    draw_subcard(51.0, 31.6, 20.5, 7.2, "#ffffff", "#a5b4fc")
    embed_crop("ntfy_phone", 59.2, 34.6, 4.0, 3.8)
    ax.text(61.25, 33.6, "Mobile Push", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#0f172a")
    ax.text(61.25, 32.6, "(ntfy.sh Instant Alert)", ha="center", va="center", fontsize=6.5, color="#64748b")

    draw_subcard(73.5, 31.6, 20.5, 7.2, "#ffffff", "#a5b4fc")
    embed_crop("system_alert_bell", 81.7, 34.6, 4.0, 3.8)
    ax.text(83.75, 33.6, "System Alerts", ha="center", va="center", fontsize=8.0, fontweight="bold", color="#0f172a")
    ax.text(83.75, 32.6, "(Through Dashboard)", ha="center", va="center", fontsize=6.5, color="#64748b")

    draw_v_arrow(50, 30.6, 29.2)

    # =========================================================================
    # 6. USER INTERFACE LAYER (Soft Aqua / Teal: #ccfbf1)
    # =========================================================================
    draw_layer_card(16.4, 12.8, "#ccfbf1", "#99f6e4")
    ax.text(50, 27.8, "6. USER INTERFACE LAYER", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#0f766e", family="sans-serif")
    ax.text(50, 26.6, "ShrimpGuard Responsive Web-based Management Dashboard", ha="center", va="center",
            fontsize=8.5, color="#0d9488", family="sans-serif")

    # 4 UI Modules
    draw_subcard(6, 17.4, 20.5, 7.8, "#ffffff", "#5eead4")
    embed_crop("ui_realtime", 14.0, 21.0, 4.5, 3.8)
    ax.text(16.25, 19.8, "Real-Time Monitoring", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0f172a")
    ax.text(16.25, 18.6, "(Live Gauges & Trends)", ha="center", va="center", fontsize=6.5, color="#64748b")

    draw_subcard(28.5, 17.4, 20.5, 7.8, "#ffffff", "#5eead4")
    embed_crop("ui_history", 36.5, 21.0, 4.5, 3.8)
    ax.text(38.75, 19.8, "Historical Trends", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0f172a")
    ax.text(38.75, 18.6, "(Date Filter & Reports)", ha="center", va="center", fontsize=6.5, color="#64748b")

    draw_subcard(51.0, 17.4, 20.5, 7.8, "#ffffff", "#5eead4")
    embed_crop("ui_ml", 59.0, 21.0, 4.5, 3.8)
    ax.text(61.25, 19.8, "Aquaculture Tools", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0f172a")
    ax.text(61.25, 18.6, "(Calculators & AI)", ha="center", va="center", fontsize=6.5, color="#64748b")

    draw_subcard(73.5, 17.4, 20.5, 7.8, "#ffffff", "#5eead4")
    embed_crop("ui_alerts", 81.5, 21.0, 4.5, 3.8)
    ax.text(83.75, 19.8, "Devices & Hardware", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0f172a")
    ax.text(83.75, 18.6, "(Hardware Diagnostics)", ha="center", va="center", fontsize=6.5, color="#64748b")

    draw_v_arrow(50, 16.4, 15.0)

    # =========================================================================
    # 7. USER DECISION MAKING (Neutral Slate / Gray: #f1f5f9)
    # =========================================================================
    draw_layer_card(4.5, 10.5, "#f1f5f9", "#cbd5e1")
    ax.text(50, 13.5, "7. USER DECISION MAKING", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color="#1e293b", family="sans-serif")
    ax.text(50, 12.2, "Enable farmers to take timely and informed actions for better aquaculture management", ha="center", va="center",
            fontsize=8.5, color="#475569", family="sans-serif")

    # 4 Action Pills
    draw_subcard(6, 5.6, 20.5, 5.4, "#ffffff", "#94a3b8")
    ax.text(16.25, 9.0, "Aeration Control", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0284c7")
    ax.text(16.25, 7.4, "(DO > 5.0 mg/L & Thermal Mix)", ha="center", va="center", fontsize=6.2, color="#475569")

    draw_subcard(28.5, 5.6, 20.5, 5.4, "#ffffff", "#94a3b8")
    ax.text(38.75, 9.0, "pH & Liming", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#16a34a")
    ax.text(38.75, 7.4, "(CaCO3 & Buffer Dosing)", ha="center", va="center", fontsize=6.2, color="#475569")

    draw_subcard(51.0, 5.6, 20.5, 5.4, "#ffffff", "#94a3b8")
    ax.text(61.25, 9.0, "Ammonia Remediation", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#ea580c")
    ax.text(61.25, 7.4, "(Molasses / Biofloc C:N)", ha="center", va="center", fontsize=6.2, color="#475569")

    draw_subcard(73.5, 5.6, 20.5, 5.4, "#ffffff", "#94a3b8")
    ax.text(83.75, 9.0, "Feed Management", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#7c3aed")
    ax.text(83.75, 7.4, "(Tray Rations & Survival)", ha="center", va="center", fontsize=6.2, color="#475569")

    # =========================================================================
    # CAPTION AT BOTTOM
    # =========================================================================
    ax.text(50, 1.8, "Figure 3. System Architectural Design", ha="center", va="center",
            fontsize=12.0, fontweight="bold", color="#0f172a", family="sans-serif")

    # Output paths
    output_png = Path("static/images/system_architecture_diagram.png")
    output_jpg = Path("static/images/system_architecture_diagram.jpg")
    artifact_png = Path(r"C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188\system_architecture_diagram.png")
    artifact_jpg = Path(r"C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188\system_architecture_diagram.jpg")

    plt.tight_layout(pad=0.2)
    fig.savefig(output_png, format="png", dpi=220, facecolor=fig.get_facecolor(), edgecolor="none")
    fig.savefig(artifact_png, format="png", dpi=220, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    # Save JPG
    img_conv = Image.open(output_png).convert("RGB")
    img_conv.save(output_jpg, format="JPEG", quality=95)
    img_conv.save(artifact_jpg, format="JPEG", quality=95)

    print("Perfected simplified diagram generated successfully!")
    print(f"  - PNG: {output_png.resolve()} ({output_png.stat().st_size} bytes)")
    print(f"  - JPG: {output_jpg.resolve()} ({output_jpg.stat().st_size} bytes)")

if __name__ == "__main__":
    generate_perfect_simplified_diagram()
