with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

target_start = "/* ==========================================================================\n   USER MANAGEMENT TOP METRICS (COMPACT BOXES WITH DISTINCT CLEAN COLOR BACKGROUNDS)\n   ========================================================================== */"
target_end = "/* ==========================================================================\n   ADMIN SETTINGS & CONFIGURATION PAGE (MATCHING SYSTEM PALETTE & REFERENCE)\n   ========================================================================== */"

start_idx = css.find(target_start)
end_idx = css.find(target_end)

if start_idx == -1 or end_idx == -1:
    print(f"Error: Could not locate targets. start_idx={start_idx}, end_idx={end_idx}")
else:
    new_css_block = '''/* ==========================================================================
   ADMIN INDICATORS / STAT METRICS: STANDARDIZED COMPACT SIZING & NON-REPEATING PALETTES
   ========================================================================== */

/* 1. Grid layout for all admin indicator sections (4-in-a-row on desktop) */
.admin-page .dashboard-metric-cards,
.admin-mgmt-main .dashboard-metric-cards {
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
    gap: 16px !important;
    margin: 0 0 20px 0 !important;
}

@media (max-width: 1200px) {
    .admin-page .dashboard-metric-cards,
    .admin-mgmt-main .dashboard-metric-cards {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 14px !important;
    }
}

@media (max-width: 600px) {
    .admin-page .dashboard-metric-cards,
    .admin-mgmt-main .dashboard-metric-cards {
        grid-template-columns: 1fr !important;
        gap: 12px !important;
    }
}

/* 2. Refined Compact Card Sizing for Admin Pages ("a bit smaller since it is just too big") */
.admin-page .dashboard-metric-card {
    padding: 16px 18px 0 !important;
    border-radius: 14px !important;
    min-height: 146px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
    transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease !important;
}

.admin-page .dashboard-metric-card .metric-card-top {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 8px !important;
    margin-bottom: 2px !important;
}

/* Squircle Icon: clean, compact (36x36px with 18px icon) */
.admin-page .dashboard-metric-card .metric-icon {
    width: 36px !important;
    height: 36px !important;
    border-radius: 10px !important;
    display: grid !important;
    place-items: center !important;
    flex-shrink: 0 !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05) !important;
}

.admin-page .dashboard-metric-card .metric-icon .ui-icon {
    width: 18px !important;
    height: 18px !important;
}

/* Category Pill Badge: sleek & compact */
.admin-page .dashboard-metric-card .metric-type {
    display: inline-flex !important;
    align-items: center !important;
    font-size: 9px !important;
    font-weight: 750 !important;
    letter-spacing: 0.6px !important;
    padding: 3px 8px !important;
    border-radius: 12px !important;
    text-transform: uppercase !important;
}

/* Card Content & Spacing */
.admin-page .dashboard-metric-card .metric-card-content {
    padding: 6px 0 8px !important;
    flex: 1 1 auto !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
}

.admin-page .dashboard-metric-card .metric-card-content h3 {
    font-size: 13px !important;
    font-weight: 700 !important;
    margin: 0 0 2px !important;
    line-height: 1.25 !important;
}

.admin-page .dashboard-metric-card .metric-reading {
    display: flex !important;
    align-items: baseline !important;
    gap: 4px !important;
    min-width: 0 !important;
}

.admin-page .dashboard-metric-card .metric-reading h2 {
    font-size: 26px !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
    line-height: 1.15 !important;
    margin: 0 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Status Pill: neat & floating */
.admin-page .dashboard-metric-card .metric-status {
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    margin: 5px 0 0 !important;
    padding: 3px 9px !important;
    border-radius: 999px !important;
    font-size: 10.5px !important;
    font-weight: 700 !important;
    line-height: 1.3 !important;
    align-self: flex-start !important;
}

.admin-page .dashboard-metric-card .metric-status::before {
    width: 6px !important;
    height: 6px !important;
    border-radius: 50% !important;
    content: "" !important;
    flex-shrink: 0 !important;
}

/* Card Footer */
.admin-page .dashboard-metric-card .metric-card-footer {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    min-height: 30px !important;
    font-size: 10.5px !important;
    font-weight: 600 !important;
    margin-top: 3px !important;
    padding: 0 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

.admin-page .dashboard-metric-card .metric-footer-dot {
    width: 5px !important;
    height: 5px !important;
    border-radius: 50% !important;
    flex-shrink: 0 !important;
}

/* --------------------------------------------------------------------------
   PALETTE 1: CLEAN SOFT SKY BLUE (ACCOUNTS / EVENTS)
   -------------------------------------------------------------------------- */
.admin-page .dashboard-metric-card.card-palette-blue {
    background: #f0f7ff !important;
    border: 1px solid #dbeafe !important;
    box-shadow: 0 2px 10px rgba(2, 132, 199, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
}
.admin-page .dashboard-metric-card.card-palette-blue:hover {
    box-shadow: 0 6px 18px rgba(2, 132, 199, 0.12) !important;
    border-color: #bfdbfe !important;
    transform: translateY(-2px) !important;
}
.admin-page .dashboard-metric-card.card-palette-blue .metric-icon {
    background: #ffffff !important;
    color: #0284c7 !important;
    box-shadow: 0 1px 4px rgba(2, 132, 199, 0.12) !important;
}
.admin-page .dashboard-metric-card.card-palette-blue .metric-type {
    background: rgba(255, 255, 255, 0.9) !important;
    color: #0369a1 !important;
    border: 1px solid rgba(186, 230, 253, 0.7) !important;
}
.admin-page .dashboard-metric-card.card-palette-blue .metric-card-content h3 {
    color: #0369a1 !important;
}
.admin-page .dashboard-metric-card.card-palette-blue .metric-reading h2 {
    color: #0c4a6e !important;
}
.admin-page .dashboard-metric-card.card-palette-blue .metric-status {
    background: #ffffff !important;
    color: #0369a1 !important;
    box-shadow: 0 1px 3px rgba(2, 132, 199, 0.10) !important;
}
.admin-page .dashboard-metric-card.card-palette-blue .metric-status::before {
    background: #0284c7 !important;
    box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.22) !important;
}
.admin-page .dashboard-metric-card.card-palette-blue .metric-card-footer {
    border-top: 1px solid rgba(186, 230, 253, 0.6) !important;
    color: #0369a1 !important;
}
.admin-page .dashboard-metric-card.card-palette-blue .metric-footer-dot {
    background: #0284c7 !important;
    box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.22) !important;
}

/* --------------------------------------------------------------------------
   PALETTE 2: CLEAN SOFT MINT GREEN (ACTIVE USERS / TELEMETRY)
   -------------------------------------------------------------------------- */
.admin-page .dashboard-metric-card.card-palette-green {
    background: #f0fdf4 !important;
    border: 1px solid #bbf7d0 !important;
    box-shadow: 0 2px 10px rgba(21, 128, 61, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
}
.admin-page .dashboard-metric-card.card-palette-green:hover {
    box-shadow: 0 6px 18px rgba(21, 128, 61, 0.12) !important;
    border-color: #86efac !important;
    transform: translateY(-2px) !important;
}
.admin-page .dashboard-metric-card.card-palette-green .metric-icon {
    background: #ffffff !important;
    color: #16a34a !important;
    box-shadow: 0 1px 4px rgba(21, 128, 61, 0.12) !important;
}
.admin-page .dashboard-metric-card.card-palette-green .metric-type {
    background: rgba(255, 255, 255, 0.9) !important;
    color: #15803d !important;
    border: 1px solid rgba(187, 247, 208, 0.7) !important;
}
.admin-page .dashboard-metric-card.card-palette-green .metric-card-content h3 {
    color: #15803d !important;
}
.admin-page .dashboard-metric-card.card-palette-green .metric-reading h2 {
    color: #14532d !important;
}
.admin-page .dashboard-metric-card.card-palette-green .metric-status {
    background: #ffffff !important;
    color: #15803d !important;
    box-shadow: 0 1px 3px rgba(21, 128, 61, 0.10) !important;
}
.admin-page .dashboard-metric-card.card-palette-green .metric-status::before {
    background: #16a34a !important;
    box-shadow: 0 0 0 2px rgba(22, 163, 74, 0.22) !important;
}
.admin-page .dashboard-metric-card.card-palette-green .metric-card-footer {
    border-top: 1px solid rgba(187, 247, 208, 0.6) !important;
    color: #15803d !important;
}
.admin-page .dashboard-metric-card.card-palette-green .metric-footer-dot {
    background: #16a34a !important;
    box-shadow: 0 0 0 2px rgba(22, 163, 74, 0.22) !important;
}

/* --------------------------------------------------------------------------
   PALETTE 3: CLEAN SOFT WARM PEACH / AMBER (INACTIVE / GATEWAY / CONTROL)
   -------------------------------------------------------------------------- */
.admin-page .dashboard-metric-card.card-palette-peach {
    background: #fff7ed !important;
    border: 1px solid #fed7aa !important;
    box-shadow: 0 2px 10px rgba(194, 65, 12, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
}
.admin-page .dashboard-metric-card.card-palette-peach:hover {
    box-shadow: 0 6px 18px rgba(194, 65, 12, 0.12) !important;
    border-color: #fdba74 !important;
    transform: translateY(-2px) !important;
}
.admin-page .dashboard-metric-card.card-palette-peach .metric-icon {
    background: #ffffff !important;
    color: #ea580c !important;
    box-shadow: 0 1px 4px rgba(194, 65, 12, 0.12) !important;
}
.admin-page .dashboard-metric-card.card-palette-peach .metric-type {
    background: rgba(255, 255, 255, 0.9) !important;
    color: #c2410c !important;
    border: 1px solid rgba(254, 215, 170, 0.7) !important;
}
.admin-page .dashboard-metric-card.card-palette-peach .metric-card-content h3 {
    color: #9a3412 !important;
}
.admin-page .dashboard-metric-card.card-palette-peach .metric-reading h2 {
    color: #7c2d12 !important;
}
.admin-page .dashboard-metric-card.card-palette-peach .metric-status {
    background: #ffffff !important;
    color: #c2410c !important;
    box-shadow: 0 1px 3px rgba(194, 65, 12, 0.10) !important;
}
.admin-page .dashboard-metric-card.card-palette-peach .metric-status::before {
    background: #ea580c !important;
    box-shadow: 0 0 0 2px rgba(234, 88, 12, 0.22) !important;
}
.admin-page .dashboard-metric-card.card-palette-peach .metric-card-footer {
    border-top: 1px solid rgba(254, 215, 170, 0.6) !important;
    color: #9a3412 !important;
}
.admin-page .dashboard-metric-card.card-palette-peach .metric-footer-dot {
    background: #ea580c !important;
    box-shadow: 0 0 0 2px rgba(234, 88, 12, 0.22) !important;
}

/* --------------------------------------------------------------------------
   PALETTE 4: CLEAN SOFT ROSE / PINK (SYSTEM HEALTH / PACKET / AUDIT)
   -------------------------------------------------------------------------- */
.admin-page .dashboard-metric-card.card-palette-rose {
    background: #fff1f2 !important;
    border: 1px solid #fecdd3 !important;
    box-shadow: 0 2px 10px rgba(225, 29, 72, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
}
.admin-page .dashboard-metric-card.card-palette-rose:hover {
    box-shadow: 0 6px 18px rgba(225, 29, 72, 0.12) !important;
    border-color: #fda4af !important;
    transform: translateY(-2px) !important;
}
.admin-page .dashboard-metric-card.card-palette-rose .metric-icon {
    background: #ffffff !important;
    color: #e11d48 !important;
    box-shadow: 0 1px 4px rgba(225, 29, 72, 0.12) !important;
}
.admin-page .dashboard-metric-card.card-palette-rose .metric-type {
    background: rgba(255, 255, 255, 0.9) !important;
    color: #be123c !important;
    border: 1px solid rgba(254, 205, 211, 0.7) !important;
}
.admin-page .dashboard-metric-card.card-palette-rose .metric-card-content h3 {
    color: #9f1239 !important;
}
.admin-page .dashboard-metric-card.card-palette-rose .metric-reading h2 {
    color: #881337 !important;
}
.admin-page .dashboard-metric-card.card-palette-rose .metric-status {
    background: #ffffff !important;
    color: #be123c !important;
    box-shadow: 0 1px 3px rgba(225, 29, 72, 0.10) !important;
}
.admin-page .dashboard-metric-card.card-palette-rose .metric-status::before {
    background: #e11d48 !important;
    box-shadow: 0 0 0 2px rgba(225, 29, 72, 0.22) !important;
}
.admin-page .dashboard-metric-card.card-palette-rose .metric-card-footer {
    border-top: 1px solid rgba(254, 205, 211, 0.6) !important;
    color: #9f1239 !important;
}
.admin-page .dashboard-metric-card.card-palette-rose .metric-footer-dot {
    background: #e11d48 !important;
    box-shadow: 0 0 0 2px rgba(225, 29, 72, 0.22) !important;
}

'''
    updated_css = css[:start_idx] + new_css_block + css[end_idx:]
    with open('static/css/style.css', 'w', encoding='utf-8') as f:
        f.write(updated_css)
    print("Successfully updated static/css/style.css")
