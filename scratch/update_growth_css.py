# -*- coding: utf-8 -*-
"""
Replace the growth CSS block in static/css/style.css with clean, uniform styles
strictly aligned with Section 1 and Section 3 calculator architecture.
"""

clean_uniform_css = '''/* ==========================================================================
   SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE CALCULATORS (Eqs. 1–8)
   Uniform styling aligned with Section 1 & Section 3 calculator architecture
   ========================================================================== */

.calculators-page .tools-tab-selector-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 22px;
    flex-wrap: wrap;
}

.calculators-page .tools-tab-selector-label {
    font-size: 11px;
    font-weight: 750;
    letter-spacing: 0.5px;
    color: #64748b;
    text-transform: uppercase;
}

.calculators-page .tools-tab-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
}

.calculators-page .growth-tab-pane {
    display: none;
    animation: fadeInSlideUp 180ms ease-out;
}

.calculators-page .growth-tab-pane.active {
    display: block;
}

.calculators-page .tools-subheading-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 14px;
    flex-wrap: wrap;
}

.calculators-page .tools-subheading-row .tools-subheading {
    margin-bottom: 0;
}
'''

def update_css():
    with open('static/css/style.css', 'r', encoding='utf-8') as f:
        content = f.read()

    marker = '/* ==========================================================================\n   SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE'
    if marker not in content:
        # try CRLF
        marker = '/* ==========================================================================\r\n   SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE'

    idx = content.find(marker)
    if idx == -1:
        print("Marker not found, appending clean CSS.")
        content += '\n\n' + clean_uniform_css
    else:
        content = content[:idx] + clean_uniform_css

    with open('static/css/style.css', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Successfully updated static/css/style.css with clean uniform growth styles!")

if __name__ == '__main__':
    update_css()

