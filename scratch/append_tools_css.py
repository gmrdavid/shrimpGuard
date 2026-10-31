css_rules = """

/* ==========================================================================
   AQUACULTURE TOOLS & CALCULATORS STYLING (SHRIMPGUARD)
   ========================================================================== */

.calculators-page .tools-sync-banner {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 18px 22px;
    background: linear-gradient(135deg, #f0fdf4 0%, #e6f7ee 100%);
    border: 1px solid #bbf7d0;
    border-radius: 14px;
    margin-bottom: 24px;
}

.calculators-page .sync-banner-info {
    display: flex;
    align-items: center;
    gap: 14px;
}

.calculators-page .sync-banner-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: #15803d;
    color: #ffffff;
    flex-shrink: 0;
}

.calculators-page .sync-banner-icon .ui-icon {
    width: 22px;
    height: 22px;
}

.calculators-page .tools-eyebrow {
    display: block;
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.8px;
    color: #166534;
    text-transform: uppercase;
    margin-bottom: 3px;
}

.calculators-page .sync-banner-info h2 {
    margin: 0 0 2px 0;
    font-size: 16px;
    font-weight: 750;
    color: #14532d;
}

.calculators-page .sync-banner-info p {
    margin: 0;
    font-size: 12.5px;
    color: #365314;
}

.calculators-page .sync-telemetry-badges {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
}

.calculators-page .telemetry-badge {
    display: flex;
    flex-direction: column;
    padding: 8px 14px;
    background: #ffffff;
    border: 1px solid #dcfce7;
    border-radius: 10px;
    min-width: 105px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.calculators-page .telemetry-label {
    font-size: 9.5px;
    font-weight: 750;
    letter-spacing: 0.5px;
    color: #4b5563;
    text-transform: uppercase;
}

.calculators-page .telemetry-value {
    font-size: 16px;
    font-weight: 800;
    color: #111827;
}

.calculators-page .telemetry-value.telemetry-status-optimal {
    color: #16a34a;
}

.calculators-page .telemetry-value.telemetry-status-warning {
    color: #d97706;
}

.calculators-page .telemetry-value.telemetry-status-critical {
    color: #dc2626;
}

.calculators-page .telemetry-substatus {
    font-size: 10px;
    font-weight: 600;
    color: #6b7280;
}

.calculators-page .telemetry-substatus.status-optimal { color: #16a34a; }
.calculators-page .telemetry-substatus.status-warning { color: #d97706; }
.calculators-page .telemetry-substatus.status-critical { color: #dc2626; }

.calculators-page .tools-btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 9px 15px;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 9px;
    color: #1e293b;
    font-size: 12.5px;
    font-weight: 650;
    cursor: pointer;
    transition: all 180ms ease;
}

.calculators-page .tools-btn-secondary:hover {
    background: #f8fafc;
    border-color: #94a3b8;
}

.calculators-page .tools-btn-secondary .ui-icon {
    width: 16px;
    height: 16px;
}

.calculators-page .tools-calc-panel {
    padding: 24px;
    margin-bottom: 24px;
}

.calculators-page .tools-panel-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 22px;
    padding-bottom: 16px;
    border-bottom: 1px solid #eef2f6;
}

.calculators-page .tools-panel-header h2 {
    margin: 0 0 3px 0;
    font-size: 17px;
    font-weight: 750;
    color: #1e293b;
}

.calculators-page .tools-panel-header p {
    margin: 0;
    font-size: 13px;
    color: #64748b;
}

.calculators-page .tools-icon-biomass {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    border-radius: 10px;
    background: #ecfdf5;
    color: #059669;
}

.calculators-page .tools-icon-lime {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: #eff6ff;
    color: #2563eb;
}

.calculators-page .tools-icon-carbon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: #fef3c7;
    color: #d97706;
}

.calculators-page .tools-icon-aerator {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: #f1f5f9;
    color: #475569;
}

.calculators-page .tools-grid-split {
    display: grid;
    grid-template-columns: 1.15fr 1fr;
    gap: 28px;
}

@media (max-width: 992px) {
    .calculators-page .tools-grid-split {
        grid-template-columns: 1fr;
    }
}

.calculators-page .tools-subheading {
    margin: 0 0 16px 0;
    font-size: 13.5px;
    font-weight: 750;
    letter-spacing: 0.3px;
    color: #334155;
    text-transform: uppercase;
}

.calculators-page .tools-form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
}

@media (max-width: 600px) {
    .calculators-page .tools-form-grid {
        grid-template-columns: 1fr;
    }
}

.calculators-page .tools-field-label {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.calculators-page .field-label-text {
    font-size: 12px;
    font-weight: 650;
    color: #475569;
}

.calculators-page .tools-field-label input,
.calculators-page .tools-select {
    width: 100%;
    padding: 10px 12px;
    font-size: 13.5px;
    font-weight: 600;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    background: #f9fafb;
    color: #111827;
    transition: all 150ms ease;
    box-sizing: border-box;
}

.calculators-page .tools-field-label input:focus,
.calculators-page .tools-select:focus {
    outline: none;
    background: #ffffff;
    border-color: #10b981;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
}

.calculators-page .tools-temp-source-box {
    grid-column: span 2;
    display: flex;
    align-items: flex-end;
    gap: 12px;
}

@media (max-width: 600px) {
    .calculators-page .tools-temp-source-box {
        grid-column: span 1;
        flex-direction: column;
        align-items: stretch;
    }
}

.calculators-page .tools-chip-btn {
    padding: 10px 14px;
    font-size: 12px;
    font-weight: 650;
    color: #047857;
    background: #d1fae5;
    border: 1px solid #a7f3d0;
    border-radius: 8px;
    cursor: pointer;
    white-space: nowrap;
    transition: all 150ms ease;
}

.calculators-page .tools-chip-btn:hover {
    background: #a7f3d0;
}

.calculators-page .tools-result-cards {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.calculators-page .tools-res-card {
    padding: 16px 18px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

.calculators-page .tools-res-card.highlight-card {
    background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
    border: 1.5px solid #6ee7b7;
}

.calculators-page .res-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 6px;
}

.calculators-page .res-card-label {
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.6px;
    color: #64748b;
    text-transform: uppercase;
}

.calculators-page .tools-res-card.highlight-card .res-card-label {
    color: #065f46;
}

.calculators-page .res-value-row {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin: 4px 0 6px 0;
}

.calculators-page .res-big-value {
    font-size: 26px;
    font-weight: 850;
    color: #0f172a;
    line-height: 1.1;
}

.calculators-page .res-accent-value {
    color: #059669;
    font-size: 28px;
}

.calculators-page .res-unit {
    font-size: 14px;
    font-weight: 650;
    color: #64748b;
}

.calculators-page .res-secondary-val {
    font-size: 13px;
    font-weight: 600;
    color: #475569;
}

.calculators-page .res-card-detail {
    margin: 0;
    font-size: 12px;
    line-height: 1.5;
    color: #475569;
}

.calculators-page .res-meal-breakdown {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    font-size: 12.5px;
    color: #065f46;
    margin-top: 6px;
    padding-top: 8px;
    border-top: 1px dashed #a7f3d0;
}

.calculators-page .res-base-note {
    font-size: 11.5px;
    color: #64748b;
}

.calculators-page .tools-callout-tip {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-top: 16px;
    padding: 12px 14px;
    background: #fefce8;
    border: 1px solid #fef08a;
    border-radius: 10px;
}

.calculators-page .tools-callout-tip .ui-icon {
    width: 18px;
    height: 18px;
    color: #ca8a04;
    flex-shrink: 0;
    margin-top: 2px;
}

.calculators-page .tools-callout-tip p {
    margin: 0;
    font-size: 12px;
    line-height: 1.55;
    color: #713f12;
}

.calculators-page .tools-treatment-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 20px;
    margin-bottom: 24px;
}

@media (max-width: 1024px) {
    .calculators-page .tools-treatment-grid {
        grid-template-columns: 1fr;
    }
}

.calculators-page .treatment-card {
    padding: 20px;
    display: flex;
    flex-direction: column;
}

.calculators-page .treatment-body {
    display: flex;
    flex-direction: column;
    gap: 16px;
    flex: 1;
}

.calculators-page .treatment-inputs {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.calculators-page .treatment-result-box {
    margin-top: auto;
    padding: 14px 16px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}

.calculators-page .treatment-instruction {
    margin: 6px 0 0 0;
    font-size: 12px;
    line-height: 1.5;
    color: #475569;
}

.calculators-page .tools-standards-panel {
    padding: 24px;
    margin-bottom: 30px;
}

.calculators-page .tools-standards-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

.calculators-page .tools-standards-table th {
    padding: 12px 14px;
    background: #f8fafc;
    color: #334155;
    font-weight: 700;
    text-align: left;
    border-bottom: 2px solid #e2e8f0;
    white-space: nowrap;
}

.calculators-page .tools-standards-table td {
    padding: 12px 14px;
    border-bottom: 1px solid #f1f5f9;
    color: #334155;
    vertical-align: middle;
}

.calculators-page .tools-standards-table tr:hover td {
    background: #f8fafc;
}

.calculators-page .param-cell-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 700;
    color: #0f172a;
}

.calculators-page .param-cell-title .ui-icon {
    width: 17px;
    height: 17px;
    color: #059669;
}

.calculators-page .tools-badge-opt {
    display: inline-block;
    padding: 4px 9px;
    font-size: 12px;
    font-weight: 750;
    color: #166534;
    background: #dcfce7;
    border: 1px solid #bbf7d0;
    border-radius: 6px;
    white-space: nowrap;
}
"""

with open('static/css/style.css', 'a', encoding='utf-8') as f:
    f.write(css_rules)

print("Appended Aquaculture Tools CSS successfully")

