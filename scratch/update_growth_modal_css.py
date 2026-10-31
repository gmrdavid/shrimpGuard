# -*- coding: utf-8 -*-
"""
Update CSS for All-in-One Growth Calculator and popup modal dialog in static/css/style.css.
"""

modal_css = '''/* ==========================================================================
   SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE CALCULATORS (Eqs. 1–8)
   Uniform styling aligned with Section 1 & Section 3 calculator architecture
   ========================================================================== */

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

.calculators-page .res-card-action-row {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed #e2e8f0;
    display: flex;
    justify-content: flex-end;
}

.calculators-page .highlight-card .res-card-action-row {
    border-top-color: #a7f3d0;
}

.calculators-page .growth-calc-details-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 13px;
    font-size: 11.5px;
    font-weight: 650;
    color: #0f766e;
    background: #f0fdfa;
    border: 1px solid #ccfbf1;
    border-radius: 7px;
    cursor: pointer;
    transition: all 130ms ease;
    outline: none;
}

.calculators-page .growth-calc-details-btn:hover {
    background: #0f766e;
    color: #ffffff;
    border-color: #0f766e;
    box-shadow: 0 1px 3px rgba(15, 118, 110, 0.25);
}

.calculators-page .growth-calc-details-btn .ui-icon {
    width: 14px;
    height: 14px;
}

.calculators-page .highlight-card .growth-calc-details-btn {
    background: #ffffff;
    border-color: #a7f3d0;
    color: #047857;
}

.calculators-page .highlight-card .growth-calc-details-btn:hover {
    background: #059669;
    color: #ffffff;
    border-color: #059669;
    box-shadow: 0 1px 3px rgba(5, 150, 105, 0.25);
}

/* Modal Popup Dialog Styles */
.growth-modal-container {
    max-width: 640px;
    width: 95%;
}

.growth-modal-body {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 22px 24px;
    max-height: 75vh;
    overflow-y: auto;
    box-sizing: border-box;
}

.growth-modal-section {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.growth-modal-section-title {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.6px;
    color: #64748b;
    text-transform: uppercase;
}

.growth-modal-formula-box {
    padding: 12px 16px;
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 9px;
    display: flex;
    align-items: center;
}

.growth-modal-formula-box code {
    font-size: 15px;
    font-weight: 750;
    color: #0f766e;
    font-family: inherit;
}

.growth-modal-vars-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 2px 4px;
    font-size: 12.5px;
    color: #475569;
    line-height: 1.45;
}

.growth-modal-vars-list strong {
    color: #1e293b;
}

.growth-modal-substitution-box {
    padding: 14px 16px;
    background: #f0fdfa;
    border: 1.5px solid #ccfbf1;
    border-radius: 9px;
}

.growth-modal-substitution-text {
    font-size: 14px;
    font-weight: 650;
    color: #115e59;
    line-height: 1.55;
    word-break: break-word;
}

.growth-modal-eval-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}

.growth-modal-eval-card {
    padding: 14px 16px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 9px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.growth-modal-eval-text {
    margin: 0;
    font-size: 13px;
    line-height: 1.55;
    color: #334155;
}

.growth-modal-tip-box {
    padding: 10px 14px;
    background: #fefce8;
    border: 1px solid #fef08a;
    border-radius: 8px;
    font-size: 12.5px;
    line-height: 1.5;
    color: #713f12;
}

.growth-modal-tip-box strong {
    color: #854d0e;
}
'''

def update_css():
    with open('static/css/style.css', 'r', encoding='utf-8') as f:
        content = f.read()

    marker = '/* ==========================================================================\n   SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE'
    if marker not in content:
        marker = '/* ==========================================================================\r\n   SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE'

    idx = content.find(marker)
    if idx == -1:
        content += '\n\n' + modal_css
    else:
        content = content[:idx] + modal_css

    with open('static/css/style.css', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Updated static/css/style.css with clean modal and card action styles!")

if __name__ == '__main__':
    update_css()

