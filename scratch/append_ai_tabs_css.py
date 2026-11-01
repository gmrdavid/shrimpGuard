css_code = """

/* AI Modal Tabs */
.ai-modal-tabs {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    background: #f1f5f9;
    padding: 4px;
    border-radius: 10px;
    margin-bottom: 14px;
}

.ai-modal-tab {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 7px;
    border: none;
    background: transparent;
    color: #475569;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.16s ease;
    white-space: nowrap;
}

.ai-modal-tab:hover {
    background: #e2e8f0;
    color: #0f172a;
}

.ai-modal-tab .ui-icon {
    width: 13px;
    height: 13px;
    fill: currentColor;
}

.ai-modal-tab.active {
    background: #15803d;
    color: #ffffff;
    box-shadow: 0 1px 4px rgba(21, 128, 61, 0.3);
}

.ai-modal-tab.active .ui-icon {
    fill: #ffffff;
    color: #ffffff;
}
"""

with open("static/css/style.css", "a", encoding="utf-8") as f:
    f.write(css_code)

print("Appended AI modal tabs CSS to static/css/style.css successfully!")

