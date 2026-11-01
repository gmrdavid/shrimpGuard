css_code = """

/* ==========================================================================
   AI DECISION SUPPORT CARDS (GEMINI AI ENGINE)
   ========================================================================== */

.tools-ai-card {
    background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-left: 4px solid #15803d;
    border-radius: 12px;
    padding: 16px 18px;
    margin-top: 18px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
    display: flex;
    flex-direction: column;
    gap: 12px;
    transition: all 0.25s ease;
}

.tools-ai-card:hover {
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    border-color: #cbd5e1;
    border-left-color: #16a34a;
}

.ai-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f1f5f9;
}

.ai-card-title-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.ai-sparkle-box {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border: 1px solid #a7f3d0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #059669;
    flex-shrink: 0;
}

.ai-sparkle-box .ui-icon {
    width: 16px;
    height: 16px;
    fill: currentColor;
}

.ai-card-eyebrow {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #15803d;
    display: block;
}

.ai-card-title {
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
    margin: 1px 0 0;
}

.ai-header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
}

.ai-status-pill {
    display: inline-flex;
    align-items: center;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

.ai-status-pill.badge-optimal {
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
}

.ai-status-pill.badge-warning {
    background: #fffbeb;
    color: #92400e;
    border: 1px solid #fde68a;
}

.ai-status-pill.badge-critical {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

.btn-generate-ai-insight {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    background: #f0fdf4;
    color: #15803d;
    border: 1px solid #86efac;
    border-radius: 7px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-generate-ai-insight:hover {
    background: #15803d;
    color: #ffffff;
    border-color: #15803d;
}

.btn-generate-ai-insight .ui-icon {
    width: 13px;
    height: 13px;
    fill: currentColor;
}

.btn-generate-ai-insight.is-loading {
    opacity: 0.75;
    pointer-events: none;
}

.btn-generate-ai-insight.is-loading .ui-icon {
    animation: aiSpin 1s linear infinite;
}

@keyframes aiSpin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.ai-card-body {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.ai-eval-text {
    font-size: 13px;
    line-height: 1.55;
    color: #334155;
    margin: 0;
}

.ai-actions-wrap {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 14px;
}

.ai-actions-title {
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.05em;
    color: #475569;
    text-transform: uppercase;
    display: block;
    margin-bottom: 6px;
}

.ai-actions-list {
    margin: 0;
    padding-left: 18px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.ai-actions-list li {
    font-size: 12.5px;
    color: #1e293b;
    line-height: 1.45;
}

.ai-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 8px;
    border-top: 1px solid #f1f5f9;
}

.ai-source-stamp {
    font-size: 10.5px;
    color: #64748b;
    font-weight: 600;
}
"""

with open("static/css/style.css", "a", encoding="utf-8") as f:
    f.write(css_code)

print("Appended AI card styles to static/css/style.css successfully!")

