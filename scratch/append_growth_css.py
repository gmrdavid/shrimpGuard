# -*- coding: utf-8 -*-
"""
Append CSS rules for Section 2 (Shrimp Growth & Zootechnical Performance Calculators) to static/css/style.css.
"""

growth_css = '''

/* ==========================================================================
   SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE CALCULATORS (Eqs. 1–8)
   ========================================================================== */

.calculators-page .growth-section {
    margin-bottom: 32px;
}

.growth-header-pills {
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Tabs Bar */
.growth-tabs-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 20px;
    padding: 6px;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

.growth-tab-item {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    background: transparent;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 140ms ease;
    white-space: nowrap;
}

.growth-tab-item:hover {
    color: #0f766e;
    background: #ffffff;
}

.growth-tab-item.active {
    color: #ffffff;
    background: #0f766e;
    box-shadow: 0 1px 3px rgba(15, 118, 110, 0.25);
}

.growth-tab-tag {
    font-size: 10.5px;
    font-weight: 700;
    padding: 2px 6px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
}

.growth-tab-item:not(.active) .growth-tab-tag {
    background: #e2e8f0;
    color: #475569;
}

/* Tab Pane Visibility */
.growth-tab-pane {
    display: none;
    animation: fadeInSlideUp 180ms ease-out;
}

.growth-tab-pane.active {
    display: block;
}

@keyframes fadeInSlideUp {
    from {
        opacity: 0;
        transform: translateY(6px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Master Panel */
.growth-master-panel,
.individual-growth-panel {
    padding: 24px;
}

.growth-pane-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    padding-bottom: 18px;
    margin-bottom: 22px;
    border-bottom: 1px solid #eef2f6;
    flex-wrap: wrap;
}

.growth-pane-title-group h3 {
    margin: 4px 0 4px 0;
    font-size: 18px;
    font-weight: 750;
    color: #1e293b;
}

.growth-pane-title-group p {
    margin: 0;
    font-size: 13px;
    color: #64748b;
    max-width: 650px;
}

.growth-card-badge {
    display: inline-block;
    font-size: 10.5px;
    font-weight: 750;
    letter-spacing: 0.5px;
    color: #0f766e;
    background: #ccfbf1;
    padding: 2px 8px;
    border-radius: 4px;
}

/* Presets */
.growth-preset-group {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
}

.growth-preset-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #64748b;
    margin-right: 2px;
}

.btn-preset-growth {
    padding: 5px 11px;
    font-size: 12px;
    font-weight: 600;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    color: #334155;
    cursor: pointer;
    transition: all 120ms ease;
}

.btn-preset-growth:hover {
    background: #f1f5f9;
    border-color: #94a3b8;
}

.btn-preset-growth.active {
    background: #0f766e;
    color: #ffffff;
    border-color: #0f766e;
}

.btn-preset-sync {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 11px;
    font-size: 12px;
    font-weight: 600;
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 6px;
    color: #047857;
    cursor: pointer;
    transition: all 120ms ease;
}

.btn-preset-sync:hover {
    background: #d1fae5;
    border-color: #6ee7b7;
}

.btn-preset-sync .ui-icon {
    width: 14px;
    height: 14px;
}

/* Master Layout */
.growth-master-layout {
    display: grid;
    grid-template-columns: 360px 1fr;
    gap: 26px;
    align-items: start;
}

.growth-input-col-title {
    margin: 0 0 14px 0;
    font-size: 13.5px;
    font-weight: 700;
    letter-spacing: 0.3px;
    color: #1e293b;
    text-transform: uppercase;
}

.growth-field-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
    margin-bottom: 18px;
}

.growth-btn-compute {
    width: 100%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 11px 18px;
    font-size: 13.5px;
    font-weight: 650;
    color: #ffffff;
    background: #0f766e;
    border: 1px solid #0f766e;
    border-radius: 9px;
    cursor: pointer;
    box-shadow: 0 1px 3px rgba(15, 118, 110, 0.25);
    transition: all 140ms ease;
}

.growth-btn-compute:hover {
    background: #115e59;
    border-color: #115e59;
}

.growth-btn-compute .ui-icon {
    width: 16px;
    height: 16px;
}

/* Master Results Grid */
.growth-cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 14px;
}

.growth-result-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 11px;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    transition: border-color 140ms ease, box-shadow 140ms ease;
}

.growth-result-card:hover {
    border-color: #cbd5e1;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.growth-res-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    flex-wrap: wrap;
}

.growth-eq-badge {
    font-size: 11px;
    font-weight: 800;
    color: #0f766e;
    background: #f0fdfa;
    border: 1px solid #ccfbf1;
    padding: 2px 6px;
    border-radius: 4px;
}

.growth-res-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.4px;
    color: #64748b;
    flex: 1;
}

.growth-sub-badge {
    font-size: 11px;
    font-weight: 650;
    color: #047857;
    background: #ecfdf5;
    padding: 2px 7px;
    border-radius: 4px;
}

.growth-res-main {
    display: flex;
    align-items: baseline;
    gap: 6px;
}

.growth-res-number {
    font-size: 26px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
    letter-spacing: -0.5px;
}

.growth-res-unit {
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
}

.growth-res-sub {
    font-size: 12px;
    color: #475569;
}

.growth-res-sub strong {
    color: #1e293b;
}

.growth-res-formula {
    margin-top: auto;
    padding-top: 8px;
    border-top: 1px dashed #e2e8f0;
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.growth-res-formula code {
    font-size: 11px;
    font-weight: 650;
    color: #0f766e;
    background: #f8fafc;
    padding: 2px 5px;
    border-radius: 4px;
    align-self: flex-start;
}

.growth-formula-sub {
    font-size: 11px;
    color: #64748b;
    font-style: italic;
}

/* Biomass Split */
.growth-biomass-split {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 0;
    font-size: 13px;
    color: #1e293b;
}

.biomass-sub-label {
    font-size: 10.5px;
    font-weight: 700;
    color: #64748b;
    display: block;
}

.biomass-arrow {
    color: #94a3b8;
    font-weight: 700;
}

/* Reference Strip */
.growth-reference-strip {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-top: 24px;
    padding: 14px 18px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}

.growth-ref-icon {
    width: 22px;
    height: 22px;
    color: #0f766e;
    flex-shrink: 0;
    margin-top: 2px;
}

.growth-ref-text {
    font-size: 12px;
    line-height: 1.55;
    color: #475569;
}

.growth-ref-text strong {
    color: #1e293b;
}

/* Individual Calculators Layout */
.indiv-calc-grid {
    display: grid;
    grid-template-columns: 360px 1fr;
    gap: 24px;
    align-items: start;
}

.indiv-calc-inputs {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.math-eq-banner {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    background: #f0fdfa;
    border: 1px solid #ccfbf1;
    border-radius: 8px;
}

.math-eq-tag {
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #0f766e;
    background: #ffffff;
    padding: 2px 6px;
    border-radius: 4px;
}

.math-eq-banner code {
    font-size: 13px;
    font-weight: 700;
    color: #115e59;
}

.indiv-calc-results {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.indiv-res-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.indiv-big-stat {
    display: flex;
    align-items: baseline;
    gap: 8px;
    flex-wrap: wrap;
}

.indiv-big-stat strong {
    font-size: 34px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1;
}

.indiv-big-stat .stat-unit {
    font-size: 16px;
    font-weight: 600;
    color: #64748b;
}

.indiv-breakdown {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding-top: 10px;
    border-top: 1px solid #e2e8f0;
}

.indiv-stat-row {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: #475569;
}

.indiv-stat-row strong {
    color: #1e293b;
    font-weight: 650;
}

.step-math-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.step-math-title {
    font-size: 12px;
    font-weight: 750;
    letter-spacing: 0.3px;
    color: #334155;
    text-transform: uppercase;
}

.step-row {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 12.5px;
    color: #64748b;
}

.step-row code {
    font-size: 12.5px;
    font-weight: 600;
    color: #0f766e;
    background: #f8fafc;
    padding: 4px 8px;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    display: block;
}

.growth-dual-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.biomass-compare-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
}

.biomass-block {
    background: #ffffff;
    padding: 14px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.biomass-block-label {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
}

.biomass-stat-val {
    font-size: 22px;
    font-weight: 800;
    color: #0f172a;
}

.biomass-stat-sub {
    font-size: 12px;
    color: #64748b;
}

.net-yield-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 14px;
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 8px;
    font-size: 13px;
    color: #047857;
}

.net-yield-banner strong {
    font-size: 15px;
    color: #065f46;
}

/* Responsive */
@media (max-width: 1024px) {
    .growth-master-layout,
    .indiv-calc-grid {
        grid-template-columns: 1fr;
    }

    .growth-cards-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 640px) {
    .growth-cards-grid,
    .growth-dual-grid,
    .biomass-compare-grid {
        grid-template-columns: 1fr;
    }

    .growth-tabs-bar {
        overflow-x: auto;
        flex-wrap: nowrap;
        -webkit-overflow-scrolling: touch;
    }

    .growth-tab-item {
        flex-shrink: 0;
    }
}
'''

def append_css():
    with open('static/css/style.css', 'r', encoding='utf-8') as f:
        content = f.read()

    marker = 'SHRIMP GROWTH & ZOOTECHNICAL PERFORMANCE CALCULATORS'
    if marker in content:
        print("CSS already appended.")
        return

    with open('static/css/style.css', 'a', encoding='utf-8') as f:
        f.write(growth_css)

    print("Successfully appended growth calculators CSS to static/css/style.css!")

if __name__ == '__main__':
    append_css()

