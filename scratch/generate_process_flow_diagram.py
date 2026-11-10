import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon
from PIL import Image

def generate_process_flow_diagram():
    # Vertical aspect ratio matching user's image (approx 10 x 18 inches @ 300 DPI -> 3000 x 5400 px)
    fig, ax = plt.subplots(figsize=(10.5, 19.0), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 190)
    ax.axis("off")

    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    # Color Palette matching user's style
    C_BLUE_BG = "#e0f2fe"       # Light blue for process boxes
    C_BLUE_BORDER = "#0284c7"   # Blue border
    C_BLUE_TEXT = "#0369a1"     # Dark blue text
    C_GREEN_BG = "#dcfce7"      # Light green for Optimal
    C_GREEN_BORDER = "#16a34a"  # Green border
    C_RED_BG = "#fee2e2"        # Light red for Alert
    C_RED_BORDER = "#dc2626"    # Red border
    C_AMBER_BG = "#ffedd5"      # Peach/orange for decision diamond
    C_AMBER_BORDER = "#ea580c"  # Orange border
    C_DARK = "#0f172a"          # Primary dark text
    C_MUTED = "#475569"         # Muted gray text

    # Helper: Stadium Pill (Terminal)
    def draw_terminal(x, y, w, h, title, subtitle):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0,rounding_size=2.0",
            facecolor="#e0f2fe",
            edgecolor="#0284c7",
            linewidth=1.8,
            zorder=3
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0f172a", family="sans-serif")
        ax.text(x + w / 2, y + h * 0.32, subtitle, ha="center", va="center", fontsize=7.2, color="#475569", family="sans-serif")

    # Helper: Process Box
    def draw_process_box(x, y, w, h, title, lines, bg_color=C_BLUE_BG, border_color=C_BLUE_BORDER):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0,rounding_size=0.8",
            facecolor=bg_color,
            edgecolor=border_color,
            linewidth=1.4,
            zorder=3
        )
        ax.add_patch(box)
        # Title
        t_y = y + h - 1.8
        ax.text(x + w / 2, t_y, title, ha="center", va="center", fontsize=8.6, fontweight="bold", color="#0f172a", family="sans-serif")
        # Sub-bullets or text lines
        line_spacing = (h - 2.8) / max(len(lines), 1)
        for idx, line in enumerate(lines):
            ly = t_y - 1.4 - idx * line_spacing
            ax.text(x + w / 2, ly, line, ha="center", va="center", fontsize=6.8, color="#334155", family="sans-serif")

    # Helper: Decision Diamond
    def draw_decision_diamond(x, y, w, h, title, subtitle):
        pts = [
            [x + w / 2, y + h],      # top
            [x + w, y + h / 2],      # right
            [x + w / 2, y],          # bottom
            [x, y + h / 2]           # left
        ]
        poly = Polygon(pts, closed=True, facecolor=C_AMBER_BG, edgecolor=C_AMBER_BORDER, linewidth=1.6, zorder=3)
        ax.add_patch(poly)
        ax.text(x + w / 2, y + h * 0.58, title, ha="center", va="center", fontsize=8.2, fontweight="bold", color="#9a3412", family="sans-serif")
        ax.text(x + w / 2, y + h * 0.38, subtitle, ha="center", va="center", fontsize=6.5, color="#c2410c", family="sans-serif")

    # Helper: Side Dashed Callout Card
    def draw_side_card(x, y, w, h, title, items, border_color="#16a34a", bg_color="#ffffff"):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0,rounding_size=0.8",
            facecolor=bg_color,
            edgecolor=border_color,
            linestyle="dashed",
            linewidth=1.4,
            zorder=3
        )
        ax.add_patch(box)
        # Title
        ax.text(x + w / 2, y + h - 1.5, title, ha="center", va="center", fontsize=7.8, fontweight="bold", color=border_color, family="sans-serif")
        # Items
        line_gap = (h - 2.5) / max(len(items), 1)
        for idx, item in enumerate(items):
            iy = y + h - 2.8 - idx * line_gap
            ax.text(x + 1.8, iy, f"• {item}", ha="left", va="center", fontsize=6.5, color="#334155", family="sans-serif")

    # Helper: Main Vertical Arrow
    def draw_arrow(x1, y1, x2, y2, color="#475569", width=1.5, label="", label_pos=None):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color=color,
                lw=width,
                mutation_scale=12,
                shrinkA=0,
                shrinkB=0
            ),
            zorder=4
        )
        if label:
            lx, ly = label_pos if label_pos else ((x1 + x2) / 2 + 1.5, (y1 + y2) / 2)
            ax.text(lx, ly, label, fontsize=7.5, fontweight="bold", color=color, va="center", ha="center")

    # Helper: Dashed Side Connector Arrow
    def draw_dashed_connector(x1, y1, x2, y2, color="#64748b"):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color=color,
                lw=1.2,
                linestyle="dashed",
                mutation_scale=10,
                shrinkA=0,
                shrinkB=0
            ),
            zorder=4
        )

    # Main Column Geometry
    MAIN_X = 26
    MAIN_W = 48
    SIDE_X = 77
    SIDE_W = 20

    # 1. START
    draw_terminal(MAIN_X + 6, 178.5, 36, 6.0, "START", "Begin system operation")
    draw_arrow(MAIN_X + 24, 178.5, MAIN_X + 24, 175.0)

    # 2. INITIALIZE SYSTEM
    draw_process_box(MAIN_X, 163.5, MAIN_W, 11.5, "INITIALIZE SYSTEM", [
        "• Power on hardware modules (Node 1 & Node 2)",
        "• Initialize ESP32, sensors, LoRa, LCD, LEDs, buzzer",
        "• Establish host serial bridge and server connection"
    ])
    draw_arrow(MAIN_X + 24, 163.5, MAIN_X + 24, 160.0)

    # 3. READ SENSORS (Sensor Node 1)
    draw_process_box(MAIN_X, 150.5, MAIN_W, 9.5, "READ SENSORS (Sensor Node 1)", [
        "Continuous pond data acquisition:",
        "Water Temperature and pH Level"
    ])
    draw_arrow(MAIN_X + 24, 150.5, MAIN_X + 24, 147.0)

    # Side Card: SENSORS USED
    draw_side_card(SIDE_X, 149.5, SIDE_W, 11.5, "SENSORS USED", [
        "Temp (DS18B20 1-Wire)",
        "pH (Analog SEN0161)",
        "Auto-temp compensated",
        "Submersible probes"
    ], border_color="#16a34a")
    draw_dashed_connector(MAIN_X + MAIN_W, 155.2, SIDE_X, 155.2, color="#16a34a")

    # 4. VALIDATE SENSOR DATA
    draw_process_box(MAIN_X, 137.5, MAIN_W, 9.5, "VALIDATE SENSOR DATA", [
        "• Check for hardware disconnection / CRC errors",
        "• Range bounds check (Temp: 10–45°C, pH: 2–12)",
        "• If out-of-range -> Flag anomaly and retry read"
    ])
    draw_arrow(MAIN_X + 24, 137.5, MAIN_X + 24, 134.0)

    # 5. PREPROCESS DATA
    draw_process_box(MAIN_X, 124.5, MAIN_W, 9.5, "PREPROCESS DATA", [
        "• Filter electrical noise via moving-average window",
        "• Convert analog voltage to pH using calibration",
        "• Format telemetry into structured binary packet"
    ])
    draw_arrow(MAIN_X + 24, 124.5, MAIN_X + 24, 121.0)

    # 6. SEND DATA VIA LoRa
    draw_process_box(MAIN_X, 112.5, MAIN_W, 8.5, "SEND DATA VIA LoRa", [
        "Sensor Node 1 (TX) -> Gateway Node 2 (RX)",
        "Chirp Spread Spectrum 433 MHz RF Broadcast"
    ])
    draw_arrow(MAIN_X + 24, 112.5, MAIN_X + 24, 109.0)

    # Side Card: COMMUNICATION
    draw_side_card(SIDE_X, 111.0, SIDE_W, 11.0, "COMMUNICATION", [
        "LoRa SX1278 (RA-02)",
        "433.5 MHz CSS",
        "Range: 1 – 5 km",
        "Ultra-low power RF"
    ], border_color="#7c3aed")
    draw_dashed_connector(MAIN_X + MAIN_W, 116.7, SIDE_X, 116.7, color="#7c3aed")

    # 7. RECEIVE DATA & LOCAL DISPLAY (Gateway Node 2)
    draw_process_box(MAIN_X, 99.5, MAIN_W, 9.5, "RECEIVE DATA (Gateway Node 2)", [
        "• LoRa receiver captures packet & unpacks payload",
        "• Measures RSSI signal strength & validates checksum",
        "• Updates 20×4 I2C Character LCD with live telemetry"
    ])
    draw_arrow(MAIN_X + 24, 99.5, MAIN_X + 24, 96.0)

    # 8. STORE DATA (Server Ingestion)
    draw_process_box(MAIN_X, 86.5, MAIN_W, 9.5, "STORE DATA", [
        "• Ingest via USB Serial CDC into Flask backend",
        "• Store record in MySQL relational database",
        "• Log timestamp, temperature, pH, and RSSI"
    ])
    draw_arrow(MAIN_X + 24, 86.5, MAIN_X + 24, 83.0)

    # Side Card: DATABASE STORAGE
    draw_side_card(SIDE_X, 85.5, SIDE_W, 11.0, "DATABASE STORAGE", [
        "MySQL Database",
        "Real-time sensor logs",
        "Historical time-series",
        "Multi-device profiles"
    ], border_color="#d97706")
    draw_dashed_connector(MAIN_X + MAIN_W, 91.2, SIDE_X, 91.2, color="#d97706")

    # 9. MACHINE LEARNING CLASSIFICATION
    draw_process_box(MAIN_X, 73.5, MAIN_W, 9.5, "MACHINE LEARNING CLASSIFICATION", [
        "Classify water quality status against trained model:",
        "Optimal  |  Warning  |  Critical"
    ])
    draw_arrow(MAIN_X + 24, 73.5, MAIN_X + 24, 69.5)

    # Side Card: ML MODEL
    draw_side_card(SIDE_X, 72.5, SIDE_W, 11.0, "ML MODEL", [
        "Scikit-Learn Classifier",
        "Optimal, Warning, Critical",
        "High accuracy validation",
        "Physiological thresholds"
    ], border_color="#7c3aed")
    draw_dashed_connector(MAIN_X + MAIN_W, 78.2, SIDE_X, 78.2, color="#7c3aed")

    # 10. DECISION DIAMOND: IS WATER QUALITY OPTIMAL?
    DEC_Y = 58.5
    draw_decision_diamond(MAIN_X + 8, DEC_Y, 32, 11.0, "IS WATER QUALITY\nOPTIMAL?", "Evaluate classification result")

    # Branch YES (Left, Green)
    draw_arrow(MAIN_X + 8, DEC_Y + 5.5, 14, DEC_Y + 5.5, color="#16a34a", width=1.6)
    draw_arrow(14, DEC_Y + 5.5, 14, 53.0, color="#16a34a", width=1.6, label="YES", label_pos=(18.5, DEC_Y + 7.5))

    draw_process_box(6, 44.5, 24, 8.5, "OPTIMAL", [
        "Maintain normal status",
        "(No corrective action required)"
    ], bg_color=C_GREEN_BG, border_color=C_GREEN_BORDER)

    draw_process_box(6, 33.5, 24, 8.5, "LOG DATA", [
        "Store nominal readings in",
        "historical trend analytics"
    ], bg_color=C_GREEN_BG, border_color=C_GREEN_BORDER)
    draw_arrow(18, 44.5, 18, 42.0, color="#16a34a")

    # Branch NO (Right, Red)
    draw_arrow(MAIN_X + 40, DEC_Y + 5.5, 66, DEC_Y + 5.5, color="#dc2626", width=1.6)
    draw_arrow(66, DEC_Y + 5.5, 66, 53.0, color="#dc2626", width=1.6, label="NO", label_pos=(61.5, DEC_Y + 7.5))

    draw_process_box(54, 44.5, 24, 8.5, "TRIGGER ALERT", [
        "Detect abnormal condition",
        "(Warning or Critical)"
    ], bg_color=C_RED_BG, border_color=C_RED_BORDER)

    draw_process_box(54, 33.5, 24, 8.5, "GET AI RECOMMENDATIONS", [
        "Query Google Gemini AI API",
        "Generate actionable remediation"
    ], bg_color=C_RED_BG, border_color=C_RED_BORDER)
    draw_arrow(66, 44.5, 66, 42.0, color="#dc2626")

    # Side Card: GEMINI AI API (attached to AI recommendations)
    draw_side_card(SIDE_X, 32.5, SIDE_W, 11.0, "GEMINI AI API", [
        "Google Gemini Engine",
        "Penaeus vannamei diagnoses",
        "Liming & aeration steps",
        "Feed adjustment guidance"
    ], border_color="#7c3aed")
    draw_dashed_connector(78, 37.7, SIDE_X, 37.7, color="#7c3aed")

    # Connect both branches down to UPDATE DASHBOARD
    draw_arrow(18, 33.5, 18, 28.0, color="#16a34a")
    draw_arrow(18, 28.0, MAIN_X + 10, 28.0, color="#16a34a")
    draw_arrow(MAIN_X + 10, 28.0, MAIN_X + 10, 25.5, color="#16a34a")

    draw_arrow(66, 33.5, 66, 28.0, color="#dc2626")
    draw_arrow(66, 28.0, MAIN_X + 38, 28.0, color="#dc2626")
    draw_arrow(MAIN_X + 38, 28.0, MAIN_X + 38, 25.5, color="#dc2626")

    # 11. UPDATE DASHBOARD
    draw_process_box(MAIN_X, 16.5, MAIN_W, 9.0, "UPDATE DASHBOARD", [
        "• Render live gauges, parameter charts, and WQI dials",
        "• Display AI recommendation cards & status badges",
        "• Update historical daily calendar indicators"
    ])
    draw_arrow(MAIN_X + 24, 16.5, MAIN_X + 24, 13.5)

    # Side Card: DASHBOARD ACCESS
    draw_side_card(SIDE_X, 15.5, SIDE_W, 10.5, "DASHBOARD ACCESS", [
        "ShrimpGuard Web App",
        "Live SVG Gauges & Dials",
        "Aquaculture Calculators",
        "Mobile-responsive UI"
    ], border_color="#d97706")
    draw_dashed_connector(MAIN_X + MAIN_W, 21.0, SIDE_X, 21.0, color="#d97706")

    # 12. ACTIVATE LOCAL & CLOUD ALERTS
    draw_process_box(MAIN_X, 5.0, MAIN_W, 8.5, "ACTIVATE LOCAL & CLOUD ALERTS", [
        "• Node 2 LEDs: Green (Optimal), Yellow (Warning), Red (Critical)",
        "• Node 2 Buzzer: Multi-cadence audible alarm (if Critical)",
        "• Instant Push: Dispatch ntfy.sh notification to smartphones"
    ])
    draw_arrow(MAIN_X + 24, 5.0, MAIN_X + 24, 2.5)

    # Side Card: HARDWARE & CLOUD ALERTS
    draw_side_card(SIDE_X, 3.5, SIDE_W, 10.5, "ALERTS & SIGNALS", [
        "Tricolor Status LEDs",
        "Active Piezo Buzzer",
        "ntfy.sh Mobile Push",
        "Web Dashboard Banners"
    ], border_color="#ea580c")
    draw_dashed_connector(MAIN_X + MAIN_W, 9.2, SIDE_X, 9.2, color="#ea580c")

    # 13. REPEAT (Bottom terminal)
    draw_terminal(MAIN_X + 6, -6.5, 36, 5.5, "REPEAT", "Continue monitoring cycle")

    # Loopback Arrow from REPEAT up to READ SENSORS
    # Route: goes left to X=3.5, goes up to Y=155.2, goes right into READ SENSORS
    ax.annotate(
        "",
        xy=(MAIN_X, 155.2),
        xytext=(3.5, 155.2),
        arrowprops=dict(
            arrowstyle="-|>",
            color="#475569",
            lw=1.5,
            mutation_scale=12,
            shrinkA=0,
            shrinkB=0
        ),
        zorder=5
    )
    ax.plot([MAIN_X + 6, 3.5, 3.5], [-3.75, -3.75, 155.2], color="#475569", lw=1.5, linestyle="solid", zorder=4)
    ax.text(4.8, 100.0, "Continuous Autonomous Monitoring Cycle (Looped Execution)",
            rotation=90, va="center", ha="left", fontsize=7.2, color="#475569", fontweight="bold")

    # Bottom Caption
    ax.text(50, -11.0, "Figure 4. Process Flow Diagram of the Proposed ShrimpGuard System",
            ha="center", va="center", fontsize=11.5, fontweight="bold", color="#0f172a", family="sans-serif")

    # Adjust limits to include negative space for bottom loop
    ax.set_ylim(-14, 188)

    plt.tight_layout(pad=0.2)

    out_dir = Path("static/images")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_png = out_dir / "process_flow_diagram.png"
    out_jpg = out_dir / "process_flow_diagram.jpg"
    
    art_dir = Path(r"C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188")
    art_png = art_dir / "process_flow_diagram.png"
    art_jpg = art_dir / "process_flow_diagram.jpg"

    fig.savefig(out_png, format="png", dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    fig.savefig(art_png, format="png", dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    img_conv = Image.open(out_png).convert("RGB")
    img_conv.save(out_jpg, format="JPEG", quality=95)
    img_conv.save(art_jpg, format="JPEG", quality=95)

    print("Process Flow Diagram generated successfully!")
    print(f"  - PNG: {out_png.resolve()} ({out_png.stat().st_size} bytes)")
    print(f"  - JPG: {out_jpg.resolve()} ({out_jpg.stat().st_size} bytes)")

if __name__ == "__main__":
    generate_process_flow_diagram()
