with open("static/css/style.css", "r", encoding="utf-8") as f:
    css = f.read()

old_css_block = """.growth-chart-wrap {
    position: relative;
    width: 100%;
    height: 320px;
    min-height: 240px;
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    box-sizing: border-box;
    overflow: visible;
    cursor: crosshair;
}

#growth-trend-chart {
    width: 100%;
    height: 100%;
    display: block;
}

#growth-chart-empty {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0;
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
}

/* Tooltip matching historical-chart-tooltip */
.growth-chart-tooltip {
    position: absolute;
    z-index: 60;
    pointer-events: none;
    box-sizing: border-box;
    width: 285px;
    padding: 10px 13px;
    border: 1px solid #dce4de;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.98);
    box-shadow: 0 12px 30px rgba(18, 107, 79, 0.14), 0 2px 8px rgba(0, 0, 0, 0.05);
    backdrop-filter: blur(8px);
    transition: opacity 120ms ease, transform 120ms ease;
}"""

new_css_block = """.growth-chart-wrap {
    position: relative;
    width: 100%;
    height: 340px;
    min-height: 260px;
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    box-sizing: border-box;
    overflow: visible;
    cursor: crosshair;
}

#growth-trend-chart {
    width: 100%;
    height: 100%;
    display: block;
    border-radius: 11px;
}

#growth-chart-empty {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0;
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
    pointer-events: none;
}

#growth-chart-empty[hidden] {
    display: none !important;
}

/* Tooltip matching historical-chart-tooltip */
.growth-chart-tooltip {
    position: absolute;
    z-index: 100;
    pointer-events: none;
    box-sizing: border-box;
    width: 290px;
    padding: 10px 14px;
    border: 1px solid #dce4de;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.98);
    box-shadow: 0 12px 32px rgba(18, 107, 79, 0.16), 0 3px 10px rgba(0, 0, 0, 0.06);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    opacity: 0;
    transform: translateY(3px);
    transition: opacity 120ms ease, transform 120ms ease;
}

.growth-chart-tooltip.visible {
    opacity: 1 !important;
    transform: translateY(0) !important;
    display: block !important;
}

.growth-chart-tooltip[hidden] {
    display: none !important;
    opacity: 0 !important;
}

.growth-chart-tooltip .tooltip-item-focused {
    background: #ecfdf5 !important;
    border-color: #a7f3d0 !important;
    box-shadow: 0 1px 3px rgba(16, 185, 129, 0.14);
}

.growth-chart-tooltip .tooltip-item-focused .tooltip-param-value {
    color: #065f46 !important;
    font-weight: 800 !important;
}"""

if old_css_block in css:
    css = css.replace(old_css_block, new_css_block)
    with open("static/css/style.css", "w", encoding="utf-8", newline="\r\n") as f:
        f.write(css)
    print("SUCCESS: Updated static/css/style.css with pointer-events: none on emptyEl, visible & hidden states, and focused styling.")
else:
    print("WARNING: old_css_block not found in style.css!")

