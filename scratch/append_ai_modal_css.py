css_modal_code = """

/* ==========================================================================
   AI DECISION SUPPORT BUTTON & MODAL
   ========================================================================== */

.tools-btn-ai-analyze {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
    color: #ffffff;
    border: 1px solid #0284c7;
    border-radius: 10px;
    padding: 9px 16px;
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(2, 132, 199, 0.28);
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.tools-btn-ai-analyze:hover {
    background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.38);
    transform: translateY(-1px);
}

.tools-btn-ai-analyze .ui-icon {
    width: 15px;
    height: 15px;
    fill: currentColor;
}

.tools-btn-ai-analyze.is-loading {
    opacity: 0.8;
    pointer-events: none;
}

.tools-btn-ai-analyze.is-loading .ui-icon {
    animation: aiBtnSpin 1s linear infinite;
}

@keyframes aiBtnSpin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Modal Dialog */
.ai-decision-dialog {
    max-width: 680px;
    width: 95%;
    border-radius: 16px;
    box-shadow: 0 20px 40px rgba(15, 23, 42, 0.22);
    overflow: hidden;
}

.ai-modal-icon {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    color: #059669;
    border: 1px solid #a7f3d0;
}

.ai-modal-context-bar {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 10px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 16px;
}

.ai-modal-context-bar .context-item {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.context-label {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.05em;
    color: #64748b;
    text-transform: uppercase;
}

.context-item strong {
    font-size: 13.5px;
    font-weight: 700;
    color: #0f172a;
}

.ai-modal-section {
    margin-bottom: 16px;
}

.ai-modal-section-title-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    color: #15803d;
}

.ai-modal-section-title-row .ui-icon {
    width: 15px;
    height: 15px;
    fill: currentColor;
}

.ai-modal-section-title {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #334155;
}

.ai-modal-eval-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #15803d;
    border-radius: 9px;
    padding: 14px 16px;
}

.ai-modal-eval-content {
    font-size: 13.5px;
    line-height: 1.6;
    color: #1e293b;
    margin: 0;
}

.ai-modal-actions-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 9px;
    padding: 12px 16px;
}

.ai-modal-actions-list {
    margin: 0;
    padding-left: 20px;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.ai-modal-actions-list li {
    font-size: 13px;
    color: #1e293b;
    line-height: 1.5;
}

.ai-modal-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    padding: 14px 22px;
    border-top: 1px solid #edf2f7;
    background: #f8fafc;
}

.ai-modal-footer-btns {
    display: flex;
    align-items: center;
    gap: 10px;
}

.btn-ai-reanalyze {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    border-radius: 8px;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    color: #0f172a;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-ai-reanalyze:hover {
    background: #f1f5f9;
    border-color: #94a3b8;
}

.btn-ai-reanalyze .ui-icon {
    width: 13px;
    height: 13px;
    fill: currentColor;
    color: #059669;
}
"""

with open("static/css/style.css", "a", encoding="utf-8") as f:
    f.write(css_modal_code)

print("Appended AI modal and button CSS successfully!")

