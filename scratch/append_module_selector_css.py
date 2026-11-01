css_content = """

/* ==========================================================================
   TOOLS & CALCULATORS MODULE SELECTOR
   ========================================================================== */

.tools-module-nav-section {
    margin-bottom: 24px;
}

.tools-module-nav-bar {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 14px 20px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}

.module-nav-header {
    display: flex;
    flex-direction: column;
}

.module-nav-eyebrow {
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #0284c7;
}

.module-nav-title {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
    margin: 2px 0 0;
}

.module-nav-controls {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}

.module-dropdown-wrap {
    position: relative;
    display: inline-block;
}

.tools-btn-choose {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
    color: #ffffff;
    border: 1px solid #0284c7;
    border-radius: 10px;
    padding: 9px 16px;
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(2, 132, 199, 0.25);
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.tools-btn-choose:hover {
    background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
    transform: translateY(-1px);
}

.tools-btn-choose .ui-icon {
    width: 16px;
    height: 16px;
    fill: currentColor;
    flex-shrink: 0;
}

.btn-choose-label {
    font-size: 12.5px;
    font-weight: 500;
    opacity: 0.92;
}

.active-computation-name {
    background: rgba(255, 255, 255, 0.22);
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.01em;
}

.tools-btn-choose .chevron-icon {
    width: 14px;
    height: 14px;
    margin-left: 2px;
    transition: transform 0.2s ease;
}

.tools-btn-choose[aria-expanded="true"] .chevron-icon {
    transform: rotate(180deg);
}

.tools-module-dropdown-menu {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    min-width: 320px;
    max-width: 360px;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    box-shadow: 0 12px 28px -4px rgba(15, 23, 42, 0.16), 0 6px 12px -2px rgba(15, 23, 42, 0.08);
    padding: 8px;
    z-index: 100;
    display: flex;
    flex-direction: column;
    gap: 4px;
    animation: moduleDropdownIn 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

.tools-module-dropdown-menu[hidden] {
    display: none !important;
}

@keyframes moduleDropdownIn {
    from {
        opacity: 0;
        transform: translateY(-6px) scale(0.98);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.module-dropdown-item {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    padding: 8px 12px;
    border: 1px solid transparent;
    background: transparent;
    border-radius: 8px;
    cursor: pointer;
    text-align: left;
    color: #1e293b;
    transition: all 0.15s ease;
}

.module-dropdown-item:hover {
    background: #f1f5f9;
}

.module-dropdown-item.active {
    background: #f0fdf4;
    border-color: #bbf7d0;
    color: #15803d;
}

.module-dropdown-item .item-icon-box {
    width: 30px;
    height: 30px;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.module-dropdown-item .item-icon-box .ui-icon {
    width: 15px;
    height: 15px;
}

.module-dropdown-item .item-meta {
    display: flex;
    flex-direction: column;
    gap: 1px;
    flex-grow: 1;
}

.module-dropdown-item .item-meta strong {
    font-size: 13px;
    font-weight: 700;
    color: #0f172a;
}

.module-dropdown-item.active .item-meta strong {
    color: #15803d;
}

.module-dropdown-item .item-meta span {
    font-size: 10.5px;
    color: #64748b;
}

.module-dropdown-item .active-check {
    margin-left: auto;
    font-size: 14px;
    font-weight: 800;
    color: #16a34a;
    display: none;
}

.module-dropdown-item.active .active-check {
    display: inline-block;
}

.module-dropdown-divider {
    height: 1px;
    background: #e2e8f0;
    margin: 4px 6px;
}

.item-icon-box.all-tools-icon {
    background: #f1f5f9;
    color: #475569;
}

/* Quick Segmented Pills */
.module-nav-pills {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    background: #f8fafc;
    padding: 4px;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}

.module-pill {
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

.module-pill:hover {
    background: #e2e8f0;
    color: #0f172a;
}

.module-pill .ui-icon {
    width: 13px;
    height: 13px;
    fill: currentColor;
}

.module-pill.active {
    background: #0284c7;
    color: #ffffff;
    box-shadow: 0 1px 3px rgba(2, 132, 199, 0.3);
}

.module-pill.active .ui-icon {
    fill: #ffffff;
    color: #ffffff;
}

.module-pill.pill-all.active {
    background: #0f172a;
    color: #ffffff;
}

/* Module Section Transition */
@keyframes calcModuleFadeIn {
    from {
        opacity: 0;
        transform: translateY(8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.calc-module-active {
    animation: calcModuleFadeIn 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}

@media (max-width: 900px) {
    .tools-module-nav-bar {
        flex-direction: column;
        align-items: stretch;
    }

    .module-nav-controls {
        flex-direction: column;
        align-items: stretch;
    }

    .tools-btn-choose {
        width: 100%;
        justify-content: space-between;
    }

    .tools-module-dropdown-menu {
        width: 100%;
        max-width: none;
    }

    .module-nav-pills {
        overflow-x: auto;
        flex-wrap: nowrap;
        padding-bottom: 6px;
    }
}
"""

with open("static/css/style.css", "a", encoding="utf-8") as f:
    f.write(css_content)

print("Appended module selector CSS to style.css successfully!")

