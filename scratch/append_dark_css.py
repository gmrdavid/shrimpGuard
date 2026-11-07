# Read the base style.css (from commit 1d940a8)
import subprocess

raw_base = subprocess.check_output(['git', 'show', '1d940a8:static/css/style.css'], text=True, encoding='utf-8')

dark_mode_css = """
/* ==========================================================================
   SHRIMPGUARD THEME SYSTEM: DARK MODE & LIGHT MODE ENGINE
   Seamless dark aquatic aesthetic across all user and admin views.
   ========================================================================== */

/* 1. Theme Toggle Button in Header */
.theme-toggle-btn {
    display: inline-grid !important;
    width: 42px !important;
    height: 42px !important;
    flex-shrink: 0 !important;
    place-items: center !important;
    border: 1px solid var(--dash-border, #e5ece7) !important;
    border-radius: 12px !important;
    background: #ffffff !important;
    color: #52675b !important;
    cursor: pointer !important;
    position: relative !important;
    z-index: 20 !important;
    outline: none !important;
    padding: 0 !important;
    transition: background-color 180ms ease, color 180ms ease, border-color 180ms ease, transform 150ms ease !important;
}

.theme-toggle-btn * {
    pointer-events: none !important;
}

.theme-toggle-btn:hover {
    background: #eaf6ef !important;
    color: #126b4f !important;
    border-color: #bce3cf !important;
    transform: translateY(-1px);
}

.theme-toggle-btn .ui-icon {
    width: 19px !important;
    height: 19px !important;
}

/* Light Mode: show Moon, hide Sun */
html:not([data-theme="dark"]):not(.theme-dark) .theme-toggle-btn .theme-icon-sun {
    display: none !important;
}
html:not([data-theme="dark"]):not(.theme-dark) .theme-toggle-btn .theme-icon-moon {
    display: block !important;
}

/* Dark Mode: show Sun, hide Moon */
html[data-theme="dark"] .theme-toggle-btn .theme-icon-sun,
html.theme-dark .theme-toggle-btn .theme-icon-sun {
    display: block !important;
}
html[data-theme="dark"] .theme-toggle-btn .theme-icon-moon,
html.theme-dark .theme-toggle-btn .theme-icon-moon {
    display: none !important;
}

/* 2. Theme CSS Variable Tokens */
html[data-theme="dark"],
html.theme-dark,
body[data-theme="dark"],
body.theme-dark {
    --dash-green: #10b981;
    --dash-green-dark: #059669;
    --dash-green-light: rgba(16, 185, 129, 0.15);
    --dash-bg: #0b1319;
    --dash-text: #e6edf1;
    --dash-muted: #8ca398;
    --dash-border: #1f333f;
    --dash-card: #121e26;

    --mon-green: #10b981;
    --mon-green-dark: #059669;
    --mon-green-light: rgba(16, 185, 129, 0.15);
    --mon-bg: #0b1319;
    --mon-text: #e6edf1;
    --mon-muted: #8ca398;
    --mon-border: #1f333f;

    --hist-green: #10b981;
    --hist-green-dark: #059669;
    --hist-green-light: rgba(16, 185, 129, 0.15);
    --hist-bg: #0b1319;
    --hist-text: #e6edf1;
    --hist-muted: #8ca398;
    --hist-border: #1f333f;

    --ana-green: #10b981;
    --ana-green-dark: #059669;
    --ana-green-light: rgba(16, 185, 129, 0.15);
    --ana-bg: #0b1319;
    --ana-text: #e6edf1;
    --ana-muted: #8ca398;
    --ana-border: #1f333f;

    --alerts-green: #10b981;
    --alerts-green-dark: #059669;
    --alerts-green-light: rgba(16, 185, 129, 0.15);
    --alerts-bg: #0b1319;
    --alerts-text: #e6edf1;
    --alerts-muted: #8ca398;
    --alerts-border: #1f333f;

    --settings-green: #10b981;
    --settings-green-dark: #059669;
    --settings-green-light: rgba(16, 185, 129, 0.15);
    --settings-bg: #0b1319;
    --settings-text: #e6edf1;
    --settings-muted: #8ca398;
    --settings-border: #1f333f;

    --sg-cream: #0b1319;
    --sg-surface: #121e26;
    --sg-surface-soft: #16252e;
    --sg-stroke: #1f333f;
    --sg-border: #1f333f;
    --sg-ink: #e6edf1;
    --sg-ink-deep: #f0f6f4;
    --sg-muted: #8ca398;
    --sg-moss: #10b981;
    --sg-moss-soft: rgba(16, 185, 129, 0.15);

    --primary: #10b981;
    --primary-dark: #059669;
    --primary-light: rgba(16, 185, 129, 0.15);
    --background: #0b1319;
    --surface: #121e26;
    --text: #e6edf1;
    --muted: #8ca398;
    --border: #1f333f;

    --admin-primary: #10b981;
    --admin-primary-dark: #059669;
    --admin-primary-light: rgba(16, 185, 129, 0.15);
    --admin-background: #0b1319;
    --admin-surface: #121e26;
    --admin-text: #e6edf1;
    --admin-muted: #8ca398;
    --admin-border: #1f333f;
}

/* 3. Dark Mode Core Body & Layout Backgrounds */
html[data-theme="dark"],
html.theme-dark,
html[data-theme="dark"] body,
html.theme-dark body,
html[data-theme="dark"] .dashboard-page,
html.theme-dark .dashboard-page,
html[data-theme="dark"] .monitoring-page,
html.theme-dark .monitoring-page,
html[data-theme="dark"] .historical-page,
html.theme-dark .historical-page,
html[data-theme="dark"] .analytics-page,
html.theme-dark .analytics-page,
html[data-theme="dark"] .alerts-page,
html.theme-dark .alerts-page,
html[data-theme="dark"] .settings-page,
html.theme-dark .settings-page,
html[data-theme="dark"] .admin-page,
html.theme-dark .admin-page,
html[data-theme="dark"] .devices-page,
html.theme-dark .devices-page,
html[data-theme="dark"] .calculators-page,
html.theme-dark .calculators-page,
html[data-theme="dark"] .login-page,
html.theme-dark .login-page,
html[data-theme="dark"] .landing-page,
html.theme-dark .landing-page {
    background-color: #0b1319 !important;
    color: #e6edf1 !important;
}

html[data-theme="dark"] .dashboard-layout,
html.theme-dark .dashboard-layout,
html[data-theme="dark"] .historical-layout-page,
html.theme-dark .historical-layout-page,
html[data-theme="dark"] .alerts-layout-page,
html.theme-dark .alerts-layout-page,
html[data-theme="dark"] .settings-layout-page,
html.theme-dark .settings-layout-page,
html[data-theme="dark"] .login-shell,
html.theme-dark .login-shell,
html[data-theme="dark"] .landing-page,
html.theme-dark .landing-page {
    background-color: #0b1319 !important;
}

/* 4. Sidebar in Dark Mode */
html[data-theme="dark"] .sidebar,
html.theme-dark .sidebar,
html[data-theme="dark"] .dashboard-sidebar,
html.theme-dark .dashboard-sidebar,
html[data-theme="dark"] .dashboard-page .dashboard-sidebar,
html.theme-dark .dashboard-page .dashboard-sidebar,
html[data-theme="dark"] .monitoring-sidebar,
html.theme-dark .monitoring-sidebar,
html[data-theme="dark"] .historical-sidebar,
html.theme-dark .historical-sidebar,
html[data-theme="dark"] .analytics-sidebar,
html.theme-dark .analytics-sidebar,
html[data-theme="dark"] .alerts-sidebar,
html.theme-dark .alerts-sidebar,
html[data-theme="dark"] .settings-sidebar,
html.theme-dark .settings-sidebar,
html[data-theme="dark"] .admin-page .sidebar,
html.theme-dark .admin-page .sidebar {
    background: #101c24 !important;
    border-right: 1px solid #1f333f !important;
    box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.02) !important;
}

html[data-theme="dark"] nav a,
html.theme-dark nav a,
html[data-theme="dark"] .dashboard-page .dashboard-nav a,
html.theme-dark .dashboard-page .dashboard-nav a,
html[data-theme="dark"] .sidebar nav a,
html.theme-dark .sidebar nav a {
    color: #9cb2a6 !important;
}

html[data-theme="dark"] nav a:hover,
html[data-theme="dark"] nav .active,
html[data-theme="dark"] .dashboard-page .dashboard-nav a:hover,
html[data-theme="dark"] .dashboard-page .dashboard-nav a.active,
html.theme-dark nav a:hover,
html.theme-dark nav .active,
html.theme-dark .dashboard-page .dashboard-nav a:hover,
html.theme-dark .dashboard-page .dashboard-nav a.active {
    background: rgba(16, 185, 129, 0.16) !important;
    border-color: rgba(16, 185, 129, 0.28) !important;
    color: #34d399 !important;
}

html[data-theme="dark"] .dashboard-page .dashboard-logo,
html.theme-dark .dashboard-page .dashboard-logo,
html[data-theme="dark"] .sidebar .logo,
html.theme-dark .sidebar .logo {
    color: #eef5f2 !important;
}

html[data-theme="dark"] .dashboard-page .dashboard-sidebar .subtitle,
html.theme-dark .dashboard-page .dashboard-sidebar .subtitle,
html[data-theme="dark"] .sidebar .subtitle,
html.theme-dark .sidebar .subtitle {
    color: #8da498 !important;
}

html[data-theme="dark"] .sidebar-help,
html.theme-dark .sidebar-help {
    background: #0d221c !important;
    border: 1px solid #16362d !important;
}

html[data-theme="dark"] .sidebar-help strong,
html.theme-dark .sidebar-help strong {
    color: #e2ece7 !important;
}

html[data-theme="dark"] .sidebar-help p,
html.theme-dark .sidebar-help p {
    color: #8da498 !important;
}

html[data-theme="dark"] .sidebar-help-icon,
html.theme-dark .sidebar-help-icon {
    background: rgba(16, 185, 129, 0.2) !important;
    color: #34d399 !important;
}

/* 5. Panels, Cards, and Containers */
html[data-theme="dark"] .panel,
html.theme-dark .panel,
html[data-theme="dark"] .card,
html.theme-dark .card,
html[data-theme="dark"] .dashboard-panel,
html.theme-dark .dashboard-panel,
html[data-theme="dark"] .monitor-card,
html.theme-dark .monitor-card,
html[data-theme="dark"] .settings-panel,
html.theme-dark .settings-panel,
html[data-theme="dark"] .admin-panel,
html.theme-dark .admin-panel,
html[data-theme="dark"] .filter-panel,
html.theme-dark .filter-panel,
html[data-theme="dark"] .wqi,
html.theme-dark .wqi,
html[data-theme="dark"] .history-review,
html.theme-dark .history-review,
html[data-theme="dark"] .readings-panel,
html.theme-dark .readings-panel,
html[data-theme="dark"] .historical-chart-panel,
html.theme-dark .historical-chart-panel,
html[data-theme="dark"] .warning-panel,
html.theme-dark .warning-panel,
html[data-theme="dark"] .input-panel,
html.theme-dark .input-panel,
html[data-theme="dark"] .ammonia-panel,
html.theme-dark .ammonia-panel,
html[data-theme="dark"] .ammonia-card,
html.theme-dark .ammonia-card,
html[data-theme="dark"] .co2-panel,
html.theme-dark .co2-panel,
html[data-theme="dark"] .calc-card,
html.theme-dark .calc-card,
html[data-theme="dark"] .tool-card,
html.theme-dark .tool-card,
html[data-theme="dark"] .devices-table-panel,
html.theme-dark .devices-table-panel,
html[data-theme="dark"] .device-category-widget,
html.theme-dark .device-category-widget,
html[data-theme="dark"] .status-ratio-card,
html.theme-dark .status-ratio-card,
html[data-theme="dark"] .landing-feature-card,
html.theme-dark .landing-feature-card,
html[data-theme="dark"] .login-panel,
html.theme-dark .login-panel,
html[data-theme="dark"] .signup-panel,
html.theme-dark .signup-panel,
html[data-theme="dark"] .dashboard-page .dashboard-metric-card,
html.theme-dark .dashboard-page .dashboard-metric-card,
html[data-theme="dark"] .monitoring-page .monitoring-reading-card,
html.theme-dark .monitoring-page .monitoring-reading-card,
html[data-theme="dark"] .analytics-page .analytics-metric-card,
html.theme-dark .analytics-page .analytics-metric-card,
html[data-theme="dark"] .alerts-page .alerts-metric-card,
html.theme-dark .alerts-page .alerts-metric-card,
html[data-theme="dark"] .analytics-page .analytics-sensor-card,
html.theme-dark .analytics-page .analytics-sensor-card,
html[data-theme="dark"] .admin-metric,
html.theme-dark .admin-metric {
    background: #121e26 !important;
    border: 1px solid #1f333f !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.35) !important;
    color: #e6edf1 !important;
}

html[data-theme="dark"] .dashboard-page .dashboard-metric-card:hover,
html.theme-dark .dashboard-page .dashboard-metric-card:hover,
html[data-theme="dark"] .monitoring-page .monitoring-reading-card:hover,
html.theme-dark .monitoring-page .monitoring-reading-card:hover,
html[data-theme="dark"] .analytics-page .analytics-metric-card:hover,
html.theme-dark .analytics-page .analytics-metric-card:hover,
html[data-theme="dark"] .alerts-page .alerts-metric-card:hover,
html.theme-dark .alerts-page .alerts-metric-card:hover,
html[data-theme="dark"] .analytics-page .analytics-sensor-card:hover,
html.theme-dark .analytics-page .analytics-sensor-card:hover {
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5) !important;
    border-color: #2b4555 !important;
}

/* 6. Typography in Dark Mode */
html[data-theme="dark"] h1,
html[data-theme="dark"] h2,
html[data-theme="dark"] h3,
html[data-theme="dark"] h4,
html[data-theme="dark"] h5,
html.theme-dark h1,
html.theme-dark h2,
html.theme-dark h3,
html.theme-dark h4,
html.theme-dark h5,
html[data-theme="dark"] .dashboard-page .dashboard-heading h1,
html.theme-dark .dashboard-page .dashboard-heading h1,
html[data-theme="dark"] .monitoring-page .monitoring-page-heading h1,
html.theme-dark .monitoring-page .monitoring-page-heading h1,
html[data-theme="dark"] .historical-page .historical-page-heading h1,
html.theme-dark .historical-page .historical-page-heading h1,
html[data-theme="dark"] .analytics-page .analytics-heading h1,
html.theme-dark .analytics-page .analytics-heading h1,
html[data-theme="dark"] .alerts-page .alerts-heading h1,
html.theme-dark .alerts-page .alerts-heading h1,
html[data-theme="dark"] .settings-page .settings-heading h1,
html.theme-dark .settings-page .settings-heading h1,
html[data-theme="dark"] .section-heading-row h2,
html.theme-dark .section-heading-row h2,
html[data-theme="dark"] .header-title h1,
html.theme-dark .header-title h1,
html[data-theme="dark"] header h1,
html.theme-dark header h1,
html[data-theme="dark"] .admin-user-header h1,
html.theme-dark .admin-user-header h1,
html[data-theme="dark"] .login-panel h1,
html.theme-dark .login-panel h1,
html[data-theme="dark"] .login-brand,
html.theme-dark .login-brand,
html[data-theme="dark"] .landing-brand,
html.theme-dark .landing-brand,
html[data-theme="dark"] .landing-copy h1,
html.theme-dark .landing-copy h1,
html[data-theme="dark"] .landing-section-heading h2,
html.theme-dark .landing-section-heading h2 {
    color: #eef5f2 !important;
}

html[data-theme="dark"] p,
html.theme-dark p,
html[data-theme="dark"] .dashboard-page .dashboard-heading > p,
html.theme-dark .dashboard-page .dashboard-heading > p,
html[data-theme="dark"] .monitoring-page .monitoring-page-heading > p,
html.theme-dark .monitoring-page .monitoring-page-heading > p,
html[data-theme="dark"] .historical-page .historical-page-heading > p,
html.theme-dark .historical-page .historical-page-heading > p,
html[data-theme="dark"] .analytics-page .analytics-heading > p,
html.theme-dark .analytics-page .analytics-heading > p,
html[data-theme="dark"] .alerts-page .alerts-heading > p,
html.theme-dark .alerts-page .alerts-heading > p,
html[data-theme="dark"] .settings-page .settings-heading > p,
html.theme-dark .settings-page .settings-heading > p,
html[data-theme="dark"] .section-heading-row p,
html.theme-dark .section-heading-row p,
html[data-theme="dark"] .landing-lead,
html.theme-dark .landing-lead {
    color: #8da498 !important;
}

html[data-theme="dark"] .eyebrow,
html.theme-dark .eyebrow,
html[data-theme="dark"] .dashboard-eyebrow,
html.theme-dark .dashboard-eyebrow,
html[data-theme="dark"] .section-eyebrow,
html.theme-dark .section-eyebrow,
html[data-theme="dark"] .monitoring-eyebrow,
html.theme-dark .monitoring-eyebrow,
html[data-theme="dark"] .historical-eyebrow,
html.theme-dark .historical-eyebrow,
html[data-theme="dark"] .analytics-eyebrow,
html.theme-dark .analytics-eyebrow,
html[data-theme="dark"] .alerts-eyebrow,
html.theme-dark .alerts-eyebrow,
html[data-theme="dark"] .settings-eyebrow,
html.theme-dark .settings-eyebrow {
    color: #34d399 !important;
}

html[data-theme="dark"] .eyebrow-dot,
html.theme-dark .eyebrow-dot,
html[data-theme="dark"] .monitoring-eyebrow-dot,
html.theme-dark .monitoring-eyebrow-dot,
html[data-theme="dark"] .historical-eyebrow-dot,
html.theme-dark .historical-eyebrow-dot {
    background: #10b981 !important;
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.22) !important;
}

/* 7. Header Controls (Theme Toggle, Notifications, Clocks) */
html[data-theme="dark"] .theme-toggle-btn,
html.theme-dark .theme-toggle-btn,
html[data-theme="dark"] .notification-button,
html.theme-dark .notification-button {
    background: #14222c !important;
    border: 1px solid #223845 !important;
    color: #a3b8ad !important;
}

html[data-theme="dark"] .theme-toggle-btn:hover,
html.theme-dark .theme-toggle-btn:hover,
html[data-theme="dark"] .notification-button:hover,
html.theme-dark .notification-button:hover {
    background: #1b2f3d !important;
    border-color: #2e4a5c !important;
    color: #34d399 !important;
}

html[data-theme="dark"] .dashboard-date-time,
html.theme-dark .dashboard-date-time,
html[data-theme="dark"] .monitoring-date-time,
html.theme-dark .monitoring-date-time,
html[data-theme="dark"] .historical-date-time,
html.theme-dark .historical-date-time,
html[data-theme="dark"] .analytics-date-time,
html.theme-dark .analytics-date-time,
html[data-theme="dark"] .alerts-date-time,
html.theme-dark .alerts-date-time,
html[data-theme="dark"] .settings-date-time,
html.theme-dark .settings-date-time,
html[data-theme="dark"] .monitoring-clock,
html.theme-dark .monitoring-clock,
html[data-theme="dark"] .historical-clock,
html.theme-dark .historical-clock {
    background: #14222c !important;
    border: 1px solid #223845 !important;
    border-radius: 12px !important;
    padding: 6px 12px !important;
}

html[data-theme="dark"] .date-time-label,
html.theme-dark .date-time-label,
html[data-theme="dark"] .monitoring-clock > span,
html.theme-dark .monitoring-clock > span,
html[data-theme="dark"] .historical-clock > span,
html.theme-dark .historical-clock > span {
    color: #7d968b !important;
}

html[data-theme="dark"] .time-value,
html.theme-dark .time-value,
html[data-theme="dark"] .monitoring-clock strong,
html.theme-dark .monitoring-clock strong,
html[data-theme="dark"] .historical-clock strong,
html.theme-dark .historical-clock strong {
    color: #eef5f2 !important;
}

/* 8. Metric Cards Details & Subcomponents */
html[data-theme="dark"] .metric-status,
html.theme-dark .metric-status,
html[data-theme="dark"] .monitoring-reading-description,
html.theme-dark .monitoring-reading-description {
    background: #162631 !important;
    border-color: #213847 !important;
    color: #9cb1a5 !important;
}

html[data-theme="dark"] .metric-card-footer,
html.theme-dark .metric-card-footer,
html[data-theme="dark"] .monitoring-reading-footer,
html.theme-dark .monitoring-reading-footer {
    border-top: 1px solid #1a2c38 !important;
    color: #778f82 !important;
}

html[data-theme="dark"] .section-count,
html.theme-dark .section-count,
html[data-theme="dark"] .monitoring-parameter-count,
html.theme-dark .monitoring-parameter-count,
html[data-theme="dark"] .historical-count-badge,
html.theme-dark .historical-count-badge,
html[data-theme="dark"] .monitoring-trend-count,
html.theme-dark .monitoring-trend-count {
    background: #162631 !important;
    border-color: #213847 !important;
    color: #9cb1a5 !important;
}

/* 9. Devices Page Elements */
html[data-theme="dark"] .devices-page .status-ratio-number,
html.theme-dark .devices-page .status-ratio-number {
    color: #34d399 !important;
}

html[data-theme="dark"] .devices-page .status-ratio-subtitle,
html.theme-dark .devices-page .status-ratio-subtitle {
    color: #8da498 !important;
}

html[data-theme="dark"] .devices-page .device-progress-track,
html.theme-dark .devices-page .device-progress-track {
    background: #1a2d3a !important;
}

html[data-theme="dark"] .devices-page .device-progress-fill,
html.theme-dark .devices-page .device-progress-fill {
    background: #10b981 !important;
}

html[data-theme="dark"] .devices-page .device-category-item,
html.theme-dark .devices-page .device-category-item {
    background: #162733 !important;
    border-color: #213948 !important;
}

html[data-theme="dark"] .devices-page .device-category-item:hover,
html.theme-dark .devices-page .device-category-item:hover {
    background: #1a2f3d !important;
}

html[data-theme="dark"] .devices-page .category-meta h4,
html.theme-dark .devices-page .category-meta h4 {
    color: #eef5f2 !important;
}

html[data-theme="dark"] .devices-page .category-meta p,
html.theme-dark .devices-page .category-meta p {
    color: #8da498 !important;
}

/* 10. Tables & Row Hover */
html[data-theme="dark"] table,
html.theme-dark table {
    background: transparent !important;
}

html[data-theme="dark"] th,
html.theme-dark th,
html[data-theme="dark"] .admin-page .uniform-table th,
html.theme-dark .admin-page .uniform-table th {
    background: #152430 !important;
    color: #8da498 !important;
    border-bottom: 1px solid #203645 !important;
}

html[data-theme="dark"] td,
html.theme-dark td,
html[data-theme="dark"] .admin-page .uniform-table td,
html.theme-dark .admin-page .uniform-table td {
    color: #d6e2dc !important;
    border-bottom: 1px solid #192b37 !important;
}

html[data-theme="dark"] tbody tr:hover td,
html.theme-dark tbody tr:hover td {
    background: rgba(255, 255, 255, 0.03) !important;
}

/* 11. Status Badges & Pills */
html[data-theme="dark"] .table-status.good,
html.theme-dark .table-status.good,
html[data-theme="dark"] .table-status.optimal,
html.theme-dark .table-status.optimal,
html[data-theme="dark"] .status-box.good,
html.theme-dark .status-box.good,
html[data-theme="dark"] .review-status,
html.theme-dark .review-status {
    background: rgba(16, 185, 129, 0.16) !important;
    color: #34d399 !important;
    border: 1px solid rgba(16, 185, 129, 0.3) !important;
}

html[data-theme="dark"] .table-status.warning,
html.theme-dark .table-status.warning,
html[data-theme="dark"] .status-box.warning,
html.theme-dark .status-box.warning,
html[data-theme="dark"] .review-warning,
html.theme-dark .review-warning,
html[data-theme="dark"] .warning-pill,
html.theme-dark .warning-pill {
    background: rgba(245, 158, 11, 0.16) !important;
    color: #fbbf24 !important;
    border: 1px solid rgba(245, 158, 11, 0.3) !important;
}

html[data-theme="dark"] .table-status.critical,
html.theme-dark .table-status.critical,
html[data-theme="dark"] .table-status.danger,
html.theme-dark .table-status.danger,
html[data-theme="dark"] .status-box.critical,
html.theme-dark .status-box.critical,
html[data-theme="dark"] .table-status.offline,
html.theme-dark .table-status.offline {
    background: rgba(239, 68, 68, 0.16) !important;
    color: #f87171 !important;
    border: 1px solid rgba(239, 68, 68, 0.3) !important;
}

html[data-theme="dark"] .table-status.demo,
html.theme-dark .table-status.demo {
    background: rgba(59, 130, 246, 0.16) !important;
    color: #60a5fa !important;
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
}

/* 12. Inputs, Selects, Forms */
html[data-theme="dark"] input,
html.theme-dark input,
html[data-theme="dark"] select,
html.theme-dark select,
html[data-theme="dark"] textarea,
html.theme-dark textarea,
html[data-theme="dark"] .quality-form input,
html.theme-dark .quality-form input,
html[data-theme="dark"] .history-filter input,
html.theme-dark .history-filter input,
html[data-theme="dark"] .history-filter select,
html.theme-dark .history-filter select,
html[data-theme="dark"] .settings-form input,
html.theme-dark .settings-form input,
html[data-theme="dark"] .admin-user-form input,
html.theme-dark .admin-user-form input,
html[data-theme="dark"] .admin-user-form select,
html.theme-dark .admin-user-form select,
html[data-theme="dark"] .admin-search input,
html.theme-dark .admin-search input,
html[data-theme="dark"] .admin-filter-label select,
html.theme-dark .admin-filter-label select,
html[data-theme="dark"] .login-form input,
html.theme-dark .login-form input,
html[data-theme="dark"] .theme-select-control,
html.theme-dark .theme-select-control {
    background: #0e181f !important;
    border: 1px solid #223847 !important;
    color: #e5ece9 !important;
}

html[data-theme="dark"] input:focus,
html.theme-dark input:focus,
html[data-theme="dark"] select:focus,
html.theme-dark select:focus,
html[data-theme="dark"] textarea:focus,
html.theme-dark textarea:focus {
    border-color: #10b981 !important;
    outline: 3px solid rgba(16, 185, 129, 0.2) !important;
}

html[data-theme="dark"] option,
html.theme-dark option {
    background: #0e181f !important;
    color: #e5ece9 !important;
}

/* 13. Modals & Overlays */
html[data-theme="dark"] .modal-overlay,
html.theme-dark .modal-overlay,
html[data-theme="dark"] .sim-modal-overlay,
html.theme-dark .sim-modal-overlay,
html[data-theme="dark"] .logout-modal-overlay,
html.theme-dark .logout-modal-overlay,
html[data-theme="dark"] .modal-dialog-overlay,
html.theme-dark .modal-dialog-overlay,
html[data-theme="dark"] .export-dialog-backdrop,
html.theme-dark .export-dialog-backdrop {
    background: rgba(3, 8, 12, 0.78) !important;
    backdrop-filter: blur(4px) !important;
}

html[data-theme="dark"] .modal-content,
html.theme-dark .modal-content,
html[data-theme="dark"] .sim-modal,
html.theme-dark .sim-modal,
html[data-theme="dark"] .logout-modal-dialog,
html.theme-dark .logout-modal-dialog,
html[data-theme="dark"] .modal-dialog-container,
html.theme-dark .modal-dialog-container,
html[data-theme="dark"] .notification-modal,
html.theme-dark .notification-modal,
html[data-theme="dark"] .notification-dropdown,
html.theme-dark .notification-dropdown,
html[data-theme="dark"] .ntfy-guide-modal,
html.theme-dark .ntfy-guide-modal {
    background: #132029 !important;
    border: 1px solid #243c4a !important;
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.6) !important;
    color: #e5ece9 !important;
}

html[data-theme="dark"] .notification-item,
html.theme-dark .notification-item {
    background: #111c24 !important;
    border-bottom: 1px solid #1a2c38 !important;
    color: #d6e2dc !important;
}

html[data-theme="dark"] .notification-item:hover,
html.theme-dark .notification-item:hover {
    background: #172733 !important;
}

html[data-theme="dark"] .notification-item.unread,
html.theme-dark .notification-item.unread {
    background: #162a38 !important;
}

/* 14. Historical Calendar & Pickers */
html[data-theme="dark"] .calendar-popup,
html.theme-dark .calendar-popup,
html[data-theme="dark"] .history-calendar-picker,
html.theme-dark .history-calendar-picker,
html[data-theme="dark"] .calendar-dropdown,
html.theme-dark .calendar-dropdown,
html[data-theme="dark"] .custom-select-menu,
html.theme-dark .custom-select-menu {
    background: #132029 !important;
    border: 1px solid #243c4a !important;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5) !important;
    color: #e5ece9 !important;
}

html[data-theme="dark"] .calendar-day,
html.theme-dark .calendar-day {
    color: #d6e2dc !important;
}

html[data-theme="dark"] .calendar-day:hover,
html.theme-dark .calendar-day:hover {
    background: #1d3240 !important;
}

html[data-theme="dark"] .calendar-day.selected,
html.theme-dark .calendar-day.selected {
    background: #126b4f !important;
    color: #ffffff !important;
}

html[data-theme="dark"] .calendar-day.other-month,
html.theme-dark .calendar-day.other-month {
    color: #4c6258 !important;
}

html[data-theme="dark"] .custom-select-option:hover,
html.theme-dark .custom-select-option:hover {
    background: #1d3240 !important;
    color: #ffffff !important;
}

/* 15. Calculators & Tools Specifics */
html[data-theme="dark"] .calc-tab,
html.theme-dark .calc-tab {
    background: #152531 !important;
    border-color: #213847 !important;
    color: #9cb1a5 !important;
}

html[data-theme="dark"] .calc-tab.active,
html.theme-dark .calc-tab.active {
    background: #126b4f !important;
    color: #ffffff !important;
    border-color: #126b4f !important;
}

html[data-theme="dark"] .calc-result-box,
html.theme-dark .calc-result-box {
    background: #162733 !important;
    border-color: #213a4a !important;
    color: #e5ece9 !important;
}

html[data-theme="dark"] .growth-chip,
html.theme-dark .growth-chip {
    background: #162733 !important;
    border-color: #213a4a !important;
    color: #9cb1a5 !important;
}

html[data-theme="dark"] .growth-chip.active,
html.theme-dark .growth-chip.active {
    background: #126b4f !important;
    color: #ffffff !important;
    border-color: #126b4f !important;
}

html[data-theme="dark"] .growth-chip:hover,
html.theme-dark .growth-chip:hover {
    background: #1c3140 !important;
}

html[data-theme="dark"] .ammonia-field-unit,
html.theme-dark .ammonia-field-unit,
html[data-theme="dark"] .calc-unit,
html.theme-dark .calc-unit,
html[data-theme="dark"] .sim-input-unit,
html.theme-dark .sim-input-unit {
    background: #162733 !important;
    border-color: #243c4a !important;
    color: #8da498 !important;
}

html[data-theme="dark"] .co2-status-banner,
html.theme-dark .co2-status-banner {
    background: #142838 !important;
    border-color: #1e3f57 !important;
}

/* 16. Admin System & Audit Terminal */
html[data-theme="dark"] .admin-logs-viewer,
html.theme-dark .admin-logs-viewer,
html[data-theme="dark"] .log-terminal,
html.theme-dark .log-terminal,
html[data-theme="dark"] .logs-code,
html.theme-dark .logs-code {
    background: #080f14 !important;
    border: 1px solid #1e323e !important;
    color: #6ee7b7 !important;
}

html[data-theme="dark"] .admin-metric-value,
html.theme-dark .admin-metric-value {
    color: #eef5f2 !important;
}

html[data-theme="dark"] .admin-metric-label,
html.theme-dark .admin-metric-label {
    color: #8da498 !important;
}

html[data-theme="dark"] .admin-metric-note,
html.theme-dark .admin-metric-note {
    color: #6b8277 !important;
}

html[data-theme="dark"] .admin-edit-user,
html.theme-dark .admin-edit-user,
html[data-theme="dark"] .admin-delete-user,
html.theme-dark .admin-delete-user,
html[data-theme="dark"] .admin-quick-action,
html.theme-dark .admin-quick-action {
    background: #162631 !important;
    border-color: #243c4a !important;
    color: #d6e2dc !important;
}

html[data-theme="dark"] .admin-edit-user:hover,
html.theme-dark .admin-edit-user:hover,
html[data-theme="dark"] .admin-quick-action:hover,
html.theme-dark .admin-quick-action:hover {
    background: #1c3140 !important;
    color: #ffffff !important;
}

/* 17. Dividers, Footnotes, Footers */
html[data-theme="dark"] .settings-panel-divider,
html.theme-dark .settings-panel-divider,
html[data-theme="dark"] .review-divider,
html.theme-dark .review-divider,
html[data-theme="dark"] .historical-review-divider,
html.theme-dark .historical-review-divider,
html[data-theme="dark"] .ammonia-card-header,
html.theme-dark .ammonia-card-header {
    background: #1d323f !important;
    border-color: #1d323f !important;
}

html[data-theme="dark"] .input-panel-footnote,
html.theme-dark .input-panel-footnote,
html[data-theme="dark"] .monitoring-recommendation-note,
html.theme-dark .monitoring-recommendation-note {
    border-top-color: #1d323f !important;
    color: #7d968b !important;
}

html[data-theme="dark"] .dashboard-footer,
html.theme-dark .dashboard-footer {
    border-top-color: #1d323f !important;
    color: #7d968b !important;
}

html[data-theme="dark"] .dashboard-footer > span:first-child,
html.theme-dark .dashboard-footer > span:first-child {
    color: #34d399 !important;
}

/* 18. Custom Scrollbars in Dark Mode */
html[data-theme="dark"] ::-webkit-scrollbar,
html.theme-dark ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
html[data-theme="dark"] ::-webkit-scrollbar-track,
html.theme-dark ::-webkit-scrollbar-track {
    background: #0b1319;
}
html[data-theme="dark"] ::-webkit-scrollbar-thumb,
html.theme-dark ::-webkit-scrollbar-thumb {
    background: #1e3543;
    border-radius: 4px;
}
html[data-theme="dark"] ::-webkit-scrollbar-thumb:hover,
html.theme-dark ::-webkit-scrollbar-thumb:hover {
    background: #2a485c;
}
"""

combined = raw_base.rstrip() + "\n\n" + dark_mode_css.strip() + "\n"

with open("static/css/style.css", "w", encoding="utf-8") as f:
    f.write(combined)

opens = combined.count('{')
closes = combined.count('}')
print(f"Total lines: {len(combined.splitlines())}, opens: {opens}, closes: {closes}")
assert opens == closes
print("SUCCESSFULLY APPLIED VERIFIED DARK MODE CSS!")
