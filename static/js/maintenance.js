/**
 * ShrimpGuard - Submerged Probe Biofilm Maintenance & Calibration Controller
 * Counteracts electrochemical sensor drift from organic biofouling in Penaeus vannamei aquaculture ponds.
 */

(function () {
    'use strict';

    let currentMaintenanceData = null;
    let cachedHistoryRecords = [];

    /**
     * Format a date string into readable local datetime.
     */
    function formatDateTime(dtStr) {
        if (!dtStr) return 'Not recorded';
        if (typeof dtStr === 'string' && dtStr.includes(',') && (dtStr.includes('AM') || dtStr.includes('PM'))) {
            return dtStr;
        }
        try {
            const normalized = dtStr.includes('T') ? dtStr : dtStr.replace(' ', 'T');
            const d = new Date(normalized);
            if (isNaN(d.getTime())) return dtStr;
            return d.toLocaleString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
        } catch (e) {
            return dtStr;
        }
    }

    /**
     * Fetch current maintenance status from backend.
     */
    async function fetchMaintenanceStatus() {
        try {
            const res = await fetch('/api/maintenance/status');
            if (!res.ok) return null;
            const data = await res.json();
            if (data && data.success && data.maintenance) {
                currentMaintenanceData = data.maintenance;
                currentMaintenanceData.is_snoozed = !!data.is_snoozed;
                renderMaintenanceBanner(currentMaintenanceData);
                renderDevicesMaintenanceCard(currentMaintenanceData);
                return currentMaintenanceData;
            }
        } catch (err) {
            console.error('Error fetching probe maintenance status:', err);
        }
        return null;
    }

    /**
     * Fetch all historical maintenance log records from backend.
     */
    async function fetchMaintenanceHistory() {
        try {
            const res = await fetch('/api/maintenance/history');
            if (!res.ok) return [];
            const data = await res.json();
            if (data && data.success && Array.isArray(data.history)) {
                cachedHistoryRecords = data.history;
                renderMaintenanceHistoryTable(cachedHistoryRecords);
                return cachedHistoryRecords;
            }
        } catch (err) {
            console.error('Error fetching probe maintenance history:', err);
        }
        return [];
    }

    /**
     * Render the table of maintenance history entries on Devices page.
     */
    function renderMaintenanceHistoryTable(historyList) {
        const tbody = document.getElementById('probe-maint-history-tbody');
        const countBadge = document.getElementById('maint-history-count-badge');

        const myEmail = (document.body.dataset.userEmail || (currentMaintenanceData && currentMaintenanceData.user_email) || '').trim().toLowerCase();
        const userHistory = (historyList || []).filter((item) => {
            if (!item) return false;
            if (myEmail && item.user_email) {
                return item.user_email.toLowerCase() === myEmail;
            }
            return true;
        });

        if (countBadge) {
            const count = userHistory ? userHistory.length : 0;
            countBadge.textContent = `${count} Logged Session${count === 1 ? '' : 's'}`;
        }

        if (!tbody) return;

        if (!userHistory || userHistory.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 24px; color: #64748b;">
                        No maintenance sessions recorded yet. Use the "Log Maintenance" button to record probe cleanings and calibrations.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = userHistory.map((item) => {
            const badgeClass = item.action === 'both' ? 'badge-optimal' : (item.action === 'cleaning' ? 'badge-warning' : 'badge-active');
            const dateStr = item.date_formatted || formatDateTime(item.performed_at);
            const devId = item.device_id || (currentMaintenanceData && currentMaintenanceData.device_id) || 'N/A';
            const tech = item.performed_by || (document.body.dataset.userName || document.body.dataset.userEmail || 'Technician');

            return `
                <tr>
                    <td style="font-weight: 600; color: #1e293b; white-space: nowrap;">
                        ${dateStr}
                    </td>
                    <td>
                        <span class="telemetry-chip chip-node" style="font-size: 11px;">
                            <svg class="ui-icon" aria-hidden="true" style="width: 12px; height: 12px;"><use href="#icon-droplet"></use></svg>
                            ${devId}
                        </span>
                    </td>
                    <td>
                        <span class="badge ${badgeClass}" style="font-size: 11.5px; font-weight: 600;">
                            ${item.maintenance_type || 'Routine Maintenance'}
                        </span>
                    </td>
                    <td style="color: #334155; font-weight: 500;">
                        ${tech}
                    </td>
                    <td style="font-size: 12.5px; color: #475569; max-width: 320px;">
                        ${item.notes || 'Routine maintenance procedure completed.'}
                    </td>
                    <td style="text-align: center;">
                        <span class="badge badge-optimal" style="font-size: 11px; padding: 3px 8px;">
                            Drift Reset (0d)
                        </span>
                    </td>
                </tr>
            `;
        }).join('');
    }

    /**
     * Render the scheduled maintenance notice banner on dashboard and monitoring pages.
     */
    function renderMaintenanceBanner(data) {
        const bannerContainer = document.getElementById('probe-maintenance-notice-container');
        if (!bannerContainer) return;

        // If user has no paired pond node, probe lifecycle timer is paused and banner is suppressed
        if (!data || !data.has_paired_node) {
            bannerContainer.style.display = 'none';
            return;
        }

        const isNoticeActive = data.is_notice_active;
        const isOverdue = data.status === 'Overdue';
        const isSnoozed = data.is_snoozed;

        if (!isNoticeActive || (isSnoozed && !isOverdue)) {
            const showOptimalBar = bannerContainer.dataset.showOptimal === 'true';
            if (showOptimalBar) {
                bannerContainer.innerHTML = `
                    <div class="maint-banner maint-banner-optimal" role="status">
                        <div class="maint-banner-left">
                            <span class="maint-banner-icon icon-optimal">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>
                            </span>
                            <div class="maint-banner-info">
                                <div class="maint-banner-eyebrow">
                                    <span class="maint-banner-tag" style="color: #15803d;">
                                        <svg class="ui-icon" aria-hidden="true" style="width: 13px; height: 13px; vertical-align: -2px;"><use href="#icon-check-circle"></use></svg>
                                        SENSOR ACCURACY ASSURED
                                    </span>
                                    <span class="maint-chip chip-optimal">Low Drift Risk</span>
                                    <span class="maint-chip chip-subtle" title="Electrochemical drift tolerance threshold">
                                        <svg class="ui-icon" aria-hidden="true" style="width: 12px; height: 12px; vertical-align: -2px;"><use href="#icon-activity"></use></svg>
                                        Target Drift: &lt; &plusmn;0.10 pH
                                    </span>
                                </div>
                                <h3 class="maint-banner-title">Sensor Probes Calibrated &amp; Biofilm-Free</h3>
                                <p class="maint-banner-desc">
                                    Submerged pond probes (pH glass bulb &amp; temperature) are within optimal operational accuracy windows.
                                    Next routine soft-brush cleaning due in <strong>${Math.max(0, Math.ceil(data.days_until_cleaning))} day(s)</strong>.
                                </p>
                            </div>
                        </div>
                        <div class="maint-banner-actions">
                            <button type="button" class="btn-maint-primary" id="btn-quick-log-maint" title="Log a probe cleaning or buffer recalibration">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-plus"></use></svg>
                                <span>Log Maintenance</span>
                            </button>
                            <div class="maint-action-group">
                                <button type="button" class="btn-maint-secondary" id="btn-open-sop-modal" title="View standard maintenance instructions">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                                    <span>Standard SOP</span>
                                </button>
                                <button type="button" class="btn-maint-secondary" id="btn-view-maint-history" title="View historical maintenance audit log">
                                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-calendar"></use></svg>
                                    <span>Audit Log</span>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                bindBannerEvents(bannerContainer);
                bannerContainer.style.display = 'block';
                return;
            } else {
                bannerContainer.style.display = 'none';
                return;
            }
        }

        // Active Notice (Due Soon or Overdue)
        const isCritical = isOverdue;
        const severityClass = isCritical ? 'maint-banner-critical' : 'maint-banner-warning';
        const iconName = isCritical ? '#icon-alert' : '#icon-clock';
        const chipClass = isCritical ? 'chip-critical' : 'chip-warning';
        const pulseClass = isCritical ? 'chip-dot-pulse-critical' : 'chip-dot-pulse';

        const cleanDaysVal = Number(data.days_until_cleaning);
        let cleanDaysRemStr = '';
        let cleanBarColor = '#d97706';
        let riskLabel = isCritical ? 'High Risk - Biofilm Drift Likely' : 'Moderate Risk - Cleaning Due';

        if (cleanDaysVal <= 0) {
            cleanDaysRemStr = `<span class="val-overdue">${Math.abs(cleanDaysVal).toFixed(1)}d Overdue</span>`;
            cleanBarColor = '#dc2626';
            riskLabel = 'Overdue - Drift Imminent';
        } else if (cleanDaysVal <= 1.2) {
            cleanDaysRemStr = `Due in 1 Day`;
            cleanBarColor = '#d97706';
            riskLabel = 'Cleaning Due in 1 Day';
        } else {
            cleanDaysRemStr = `${cleanDaysVal.toFixed(1)}d Remaining`;
            cleanBarColor = cleanDaysVal <= 2 ? '#d97706' : '#126b4f';
        }

        const calDaysVal = Number(data.days_until_calibration);
        let calDaysRemStr = '';
        let calBarColor = '#0284c7';
        if (calDaysVal <= 0) {
            calDaysRemStr = `<span class="val-overdue">${Math.abs(calDaysVal).toFixed(1)}d Overdue</span>`;
            calBarColor = '#dc2626';
        } else if (calDaysVal <= 2) {
            calDaysRemStr = `Due in ${Math.max(1, Math.round(calDaysVal))}d`;
            calBarColor = '#d97706';
        } else {
            calDaysRemStr = `${calDaysVal.toFixed(1)}d Remaining`;
            calBarColor = '#0284c7';
        }

        const cleanPct = Math.min(100, Math.max(0, data.cleaning_progress_pct || 0));
        const calPct = Math.min(100, Math.max(0, data.calibration_progress_pct || 0));

        bannerContainer.innerHTML = `
            <div class="maint-banner ${severityClass}" role="alert">
                <div class="maint-banner-left">
                    <span class="maint-banner-icon" aria-hidden="true">
                        <svg class="ui-icon"><use href="${iconName}"></use></svg>
                    </span>
                    <div class="maint-banner-info">
                        <div class="maint-banner-eyebrow">
                            <span class="maint-banner-tag">
                                <svg class="ui-icon" aria-hidden="true" style="width: 13px; height: 13px; vertical-align: -2px;"><use href="#icon-clock"></use></svg>
                                PROBE ACCURACY ALERT
                            </span>
                            <span class="maint-chip ${chipClass}">
                                <span class="${pulseClass}"></span>
                                ${riskLabel}
                            </span>
                            <span class="maint-chip chip-subtle" title="Electrochemical drift tolerance threshold">
                                <svg class="ui-icon" aria-hidden="true" style="width: 12px; height: 12px; vertical-align: -2px;"><use href="#icon-activity"></use></svg>
                                Target Drift: &lt; &plusmn;0.10 pH
                            </span>
                        </div>

                        <h3 class="maint-banner-title">${data.notice_title}</h3>

                        <div class="maint-stats-row">
                            <!-- 7-Day Biofilm Scrubbing Cycle Widget -->
                            <div class="maint-stat-pill">
                                <div class="maint-stat-pill-header">
                                    <span class="maint-stat-label">
                                        <svg class="ui-icon icon-droplet" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                                        Biofilm Scrub (7d)
                                    </span>
                                    <strong class="maint-stat-value">${cleanDaysRemStr}</strong>
                                </div>
                                <div class="maint-mini-track">
                                    <div class="maint-mini-fill" style="width: ${cleanPct}%; background-color: ${cleanBarColor};"></div>
                                </div>
                                <div class="maint-stat-sub">
                                    <span>Submerged: <strong>${data.days_since_cleaning != null ? data.days_since_cleaning + 'd' : '6d'}</strong></span>
                                    <span>${cleanPct}% of cycle</span>
                                </div>
                            </div>

                            <!-- 14-Day 2-Point Buffer Calibration Widget -->
                            <div class="maint-stat-pill">
                                <div class="maint-stat-pill-header">
                                    <span class="maint-stat-label">
                                        <svg class="ui-icon icon-settings" aria-hidden="true"><use href="#icon-settings"></use></svg>
                                        2-Pt pH Calibration (14d)
                                    </span>
                                    <strong class="maint-stat-value val-blue">${calDaysRemStr}</strong>
                                </div>
                                <div class="maint-mini-track">
                                    <div class="maint-mini-fill fill-blue" style="width: ${calPct}%; background-color: ${calBarColor};"></div>
                                </div>
                                <div class="maint-stat-sub">
                                    <span>Elapsed: <strong>${data.days_since_calibration != null ? data.days_since_calibration + 'd' : '12d'}</strong></span>
                                    <span>${calPct}% of cycle</span>
                                </div>
                            </div>

                            <!-- Last Maintained Meta Widget -->
                            <div class="maint-stat-pill maint-stat-pill-meta">
                                <div class="maint-stat-pill-header">
                                    <span class="maint-stat-label">
                                        <svg class="ui-icon icon-calendar" aria-hidden="true"><use href="#icon-calendar"></use></svg>
                                        Last Recorded Action
                                    </span>
                                    <span class="maint-meta-node-badge">Node 1</span>
                                </div>
                                <div class="maint-meta-action-name">${data.maintenance_type || 'Biofilm Cleaning & 2-Pt Cal'}</div>
                                <div class="maint-stat-sub">
                                    <span>${formatDateTime(data.last_cleaned_at)}</span>
                                    <strong>${data.performed_by || 'Pond Operator'}</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="maint-banner-actions">
                    <button type="button" class="btn-maint-primary" id="btn-quick-log-maint" title="Record completed cleaning or calibration">
                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>
                        <span>Mark Cleaned &amp; Calibrated</span>
                    </button>
                    <div class="maint-action-group">
                        <button type="button" class="btn-maint-secondary" id="btn-open-sop-modal" title="View step-by-step cleaning and 2-point calibration protocol">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-lightbulb"></use></svg>
                            <span>Standard SOP</span>
                        </button>
                        <button type="button" class="btn-maint-secondary" id="btn-view-maint-history" title="View historical maintenance audit log">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-calendar"></use></svg>
                            <span>Audit Log</span>
                        </button>
                    </div>
                    <button type="button" class="btn-maint-dismiss" id="btn-dismiss-maint" title="Snooze maintenance notice for 24 hours">
                        <svg class="ui-icon" aria-hidden="true" style="width: 12px; height: 12px; margin-right: 4px;"><use href="#icon-clock"></use></svg>
                        <span>Snooze Notice for 24h</span>
                    </button>
                </div>
            </div>
        `;

        bannerContainer.style.display = 'block';
        bindBannerEvents(bannerContainer);
    }

    /**
     * Render the dedicated lifecycle card on the Devices & Hardware page.
     */
    function renderDevicesMaintenanceCard(data) {
        const cardContainer = document.getElementById('probe-maintenance-devices-card');
        if (!cardContainer || !data) return;

        const hasNode = !!data.has_paired_node;
        const isOverdue = data.status === 'Overdue';
        const isDueSoon = data.status === 'Due Soon';
        const badgeClass = !hasNode ? 'badge-secondary' : (isOverdue ? 'badge-critical' : (isDueSoon ? 'badge-warning' : 'badge-optimal'));
        const badgeText = !hasNode ? 'AWAITING PAIRED NODE' : (isOverdue ? 'OVERDUE - BIOFILM DRIFT' : (isDueSoon ? 'MAINTENANCE DUE SOON' : 'CALIBRATED & HEALTHY'));

        const cleanPct = !hasNode ? 0 : Math.min(100, Math.max(0, data.cleaning_progress_pct || 0));
        const calPct = !hasNode ? 0 : Math.min(100, Math.max(0, data.calibration_progress_pct || 0));

        const cleanBarColor = !hasNode ? '#94a3b8' : (cleanPct >= 100 ? '#dc2626' : (cleanPct >= 75 ? '#d97706' : '#126b4f'));
        const calBarColor = !hasNode ? '#94a3b8' : (calPct >= 100 ? '#dc2626' : (calPct >= 75 ? '#d97706' : '#0284c7'));

        const riskSlug = !hasNode ? 'standby' : (data.status || 'optimal').toLowerCase().replace(/\s+/g, '-');
        const driftRiskText = data.drift_risk || (hasNode ? 'Low Risk - Probes Calibrated & Clean' : 'Timer Paused — Pair a pond telemetry node to activate anti-drift tracking');

        const cleanSubmergedText = !hasNode ? 'Timer Paused' : `${data.days_since_cleaning != null ? data.days_since_cleaning : 0} days`;
        const cleanDueText = !hasNode ? 'Awaiting Node' : ((data.days_until_cleaning != null && data.days_until_cleaning > 0) ? `${data.days_until_cleaning}d` : 'NOW');

        const calElapsedText = !hasNode ? 'Timer Paused' : `${data.days_since_calibration != null ? data.days_since_calibration : 0} days`;
        const calDueText = !hasNode ? 'Awaiting Node' : ((data.days_until_calibration != null && data.days_until_calibration > 0) ? `${data.days_until_calibration}d` : 'NOW');

        const subtitleText = hasNode
            ? `Anti-drift tracking for ${data.device_id || 'Node 1'} submerged DFRobot pH probe &amp; DS18B20 temperature probe`
            : `Anti-drift tracking paused. Pair a pond telemetry node to start biofilm &amp; calibration lifecycle schedules.`;

        let lastActionHtml = '';
        if (!hasNode || !data.last_cleaned_at || data.performed_by === 'N/A') {
            lastActionHtml = `
                <span>Last Recorded Action: <strong style="color: #334155;">No maintenance recorded yet</strong> by <strong style="color: #334155;">N/A</strong></span>
                <span style="margin-left: 12px; color: #94a3b8;">(Timer starts upon node pairing)</span>
            `;
        } else {
            lastActionHtml = `
                <span>Last Recorded Action: <strong style="color: #334155;">${data.maintenance_type || 'Routine Inspection'}</strong> by <strong style="color: #334155;">${data.performed_by || 'Technician'}</strong></span>
                <span style="margin-left: 12px; color: #94a3b8;">(${formatDateTime(data.last_cleaned_at)})</span>
            `;
        }

        cardContainer.innerHTML = `
            <article class="panel dashboard-panel probe-lifecycle-card">
                <div class="panel-heading" style="justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div style="display: flex; align-items: center; gap: 11px;">
                        <div class="panel-heading-icon" style="background: #f0fdf4; color: #126b4f;">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                        </div>
                        <div>
                            <h2 style="font-size: 16px; margin: 0; color: #1e293b;">Submerged Probe Biofilm &amp; Calibration Lifecycle</h2>
                            <p style="margin: 2px 0 0; font-size: 12px; color: #64748b;">
                                ${subtitleText}
                            </p>
                        </div>
                    </div>
                    <span class="badge ${badgeClass}" style="font-size: 12px; font-weight: 700; padding: 5px 12px;">
                        ${badgeText}
                    </span>
                </div>

                <div class="probe-lifecycle-body" style="padding: 18px 20px;">
                    <!-- Drift Risk Indicator Strip -->
                    <div class="drift-risk-banner risk-${riskSlug}" style="margin-bottom: 18px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <svg class="ui-icon" aria-hidden="true" style="width: 18px; height: 18px;"><use href="#icon-activity"></use></svg>
                            <strong>Drift Risk Assessment:</strong>
                            <span>${driftRiskText}</span>
                        </div>
                        <span style="font-size: 12px; color: #475569;">Target Drift: &lt; &plusmn;0.10 pH</span>
                    </div>

                    <div class="probe-cycles-grid">
                        <!-- 7-Day Routine Biofilm Cleaning Cycle -->
                        <div class="probe-cycle-box">
                            <div class="probe-cycle-header">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <svg class="ui-icon" style="width: 16px; height: 16px; fill: #126b4f;"><use href="#icon-droplet"></use></svg>
                                    <strong style="font-size: 13px; color: #1e293b;">7-Day Biofilm Scrubbing Cycle</strong>
                                </div>
                                <span style="font-size: 12px; font-weight: 700; color: ${cleanBarColor};">${cleanPct}%</span>
                            </div>
                            <div class="maint-progress-track">
                                <div class="maint-progress-fill" style="width: ${cleanPct}%; background-color: ${cleanBarColor};"></div>
                            </div>
                            <div class="probe-cycle-meta">
                                <span>Submerged: <strong>${cleanSubmergedText}</strong></span>
                                <span>Next Due: <strong>${cleanDueText}</strong></span>
                            </div>
                        </div>

                        <!-- 14-Day 2-Point Buffer Recalibration Cycle -->
                        <div class="probe-cycle-box">
                            <div class="probe-cycle-header">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <svg class="ui-icon" style="width: 16px; height: 16px; fill: #0284c7;"><use href="#icon-settings"></use></svg>
                                    <strong style="font-size: 13px; color: #1e293b;">14-Day 2-Point pH Calibration</strong>
                                </div>
                                <span style="font-size: 12px; font-weight: 700; color: ${calBarColor};">${calPct}%</span>
                            </div>
                            <div class="maint-progress-track">
                                <div class="maint-progress-fill" style="width: ${calPct}%; background-color: ${calBarColor};"></div>
                            </div>
                            <div class="probe-cycle-meta">
                                <span>Elapsed: <strong>${calElapsedText}</strong></span>
                                <span>Next Due: <strong>${calDueText}</strong></span>
                            </div>
                        </div>
                    </div>

                    <!-- Last Maintenance Log Info -->
                    <div class="probe-maint-history-row" style="margin-top: 16px; padding-top: 14px; border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                        <div style="font-size: 12px; color: #64748b;">
                            ${lastActionHtml}
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button type="button" class="btn-maint-secondary" id="btn-devices-open-sop" style="font-size: 12px; padding: 6px 12px;" title="View standard maintenance SOP guide">
                                <svg class="ui-icon" aria-hidden="true" style="width: 14px; height: 14px;"><use href="#icon-lightbulb"></use></svg>
                                <span>Standard SOP</span>
                            </button>
                            <button type="button" class="btn-maint-secondary" id="btn-devices-view-history" style="font-size: 12px; padding: 6px 12px;" title="Open Probe Maintenance & Calibration Audit Log pop-up dialog">
                                <svg class="ui-icon" aria-hidden="true" style="width: 14px; height: 14px;"><use href="#icon-calendar"></use></svg>
                                <span>Audit Log Dialog</span>
                            </button>
                            ${!hasNode
                                ? `<button type="button" class="btn-maint-primary btn-maint-disabled" id="btn-devices-log-maint" style="font-size: 12px; padding: 6px 14px; opacity: 0.55; cursor: not-allowed;" title="Pair a pond telemetry node to enable probe maintenance (biofilm scrubbing &amp; 2-point pH calibration)" disabled>
                                    <svg class="ui-icon" aria-hidden="true" style="width: 14px; height: 14px;"><use href="#icon-lock"></use></svg>
                                    <span>Log Maintenance</span>
                                   </button>`
                                : `<button type="button" class="btn-maint-primary" id="btn-devices-log-maint" style="font-size: 12px; padding: 6px 14px;" title="Log probe biofilm scrubbing or 2-point pH buffer calibration">
                                    <svg class="ui-icon" aria-hidden="true" style="width: 14px; height: 14px;"><use href="#icon-plus"></use></svg>
                                    <span>Log Maintenance</span>
                                   </button>`
                            }
                        </div>
                    </div>
                </div>
            </article>
        `;

        const logBtn = cardContainer.querySelector('#btn-devices-log-maint');
        if (logBtn) {
            logBtn.addEventListener('click', (e) => {
                if (!currentMaintenanceData || !currentMaintenanceData.has_paired_node) {
                    e.preventDefault();
                    showMaintenanceToast('Cannot log maintenance: Probe maintenance (biofilm scrubbing cycle & 2-point pH calibration) requires an active paired pond telemetry node. Please pair a node first.');
                    const pairBtn = document.getElementById('btn-open-pair-modal');
                    if (pairBtn) pairBtn.click();
                    return;
                }
                openMaintenanceModal('both');
            });
        }

        const sopBtn = cardContainer.querySelector('#btn-devices-open-sop');
        if (sopBtn) sopBtn.addEventListener('click', openSOPModal);

        const histBtn = cardContainer.querySelector('#btn-devices-view-history');
        if (histBtn) histBtn.addEventListener('click', openHistoryModal);
    }

    /**
     * Bind click events on the banner buttons.
     */
    function bindBannerEvents(container) {
        const logBtn = container.querySelector('#btn-quick-log-maint');
        if (logBtn) {
            logBtn.addEventListener('click', () => openMaintenanceModal('both'));
        }

        const sopBtn = container.querySelector('#btn-open-sop-modal');
        if (sopBtn) {
            sopBtn.addEventListener('click', openSOPModal);
        }

        const histBtn = container.querySelector('#btn-view-maint-history');
        if (histBtn) {
            histBtn.addEventListener('click', openHistoryModal);
        }

        const dismissBtn = container.querySelector('#btn-dismiss-maint');
        if (dismissBtn) {
            dismissBtn.addEventListener('click', dismissMaintenanceNotice);
        }
    }

    /**
     * Snooze/dismiss the maintenance banner for 24 hours.
     */
    async function dismissMaintenanceNotice() {
        try {
            const res = await fetch('/api/maintenance/dismiss', { method: 'POST' });
            if (res.ok) {
                const bannerContainer = document.getElementById('probe-maintenance-notice-container');
                if (bannerContainer) {
                    bannerContainer.style.opacity = '0';
                    setTimeout(() => {
                        bannerContainer.style.display = 'none';
                        bannerContainer.style.opacity = '1';
                    }, 300);
                }
            }
        } catch (err) {
            console.error('Failed to dismiss maintenance notice:', err);
        }
    }

    /**
     * Open the SOP modal dialog.
     */
    function openSOPModal() {
        let modal = document.getElementById('probe-maint-sop-modal');
        if (!modal) {
            createSOPModalElement();
            modal = document.getElementById('probe-maint-sop-modal');
        }
        if (modal) {
            const hasNode = !!(currentMaintenanceData && currentMaintenanceData.has_paired_node);
            const proceedBtn = modal.querySelector('#btn-sop-proceed-log');
            if (proceedBtn) {
                if (!hasNode) {
                    proceedBtn.disabled = true;
                    proceedBtn.classList.add('btn-maint-disabled');
                    proceedBtn.style.opacity = '0.55';
                    proceedBtn.style.cursor = 'not-allowed';
                    proceedBtn.title = 'Pair a pond telemetry node to enable probe maintenance (biofilm scrubbing & 2-point pH calibration)';
                } else {
                    proceedBtn.disabled = false;
                    proceedBtn.classList.remove('btn-maint-disabled');
                    proceedBtn.style.opacity = '1';
                    proceedBtn.style.cursor = 'pointer';
                    proceedBtn.title = 'Proceed to log probe biofilm scrubbing or buffer recalibration';
                }
            }
            modal.removeAttribute('hidden');
            modal.classList.add('is-open');
            document.body.classList.add('modal-backdrop-open');
        }
    }

    /**
     * Close the SOP modal dialog.
     */
    function closeSOPModal() {
        const modal = document.getElementById('probe-maint-sop-modal');
        if (modal) {
            modal.classList.remove('is-open');
            modal.setAttribute('hidden', '');
            document.body.classList.remove('modal-backdrop-open');
        }
    }

    /**
     * Dynamically update modal fields to prevent stale or cross-account data leaks.
     */
    function updateLogModalDynamicFields(modal) {
        if (!modal) return;
        const activeNodeId = (currentMaintenanceData && currentMaintenanceData.has_paired_node && currentMaintenanceData.device_id)
            ? currentMaintenanceData.device_id
            : '';
        const userEmail = (document.body.dataset.userEmail || (currentMaintenanceData && currentMaintenanceData.user_email) || '').trim();
        const userName = (document.body.dataset.userName || '').trim();
        const defaultTech = userName || userEmail || 'Pond Operator';

        const devInput = modal.querySelector('input[name="device_id"]');
        if (devInput) devInput.value = activeNodeId;

        const badgeEl = modal.querySelector('.maint-target-id-badge');
        if (badgeEl) badgeEl.textContent = activeNodeId || 'No Paired Node';

        const techInput = modal.querySelector('#maint-technician-input');
        if (techInput) {
            techInput.value = defaultTech;
        }

        const dateInput = modal.querySelector('#maint-datetime-input');
        if (dateInput) {
            const now = new Date();
            const pad = (n) => String(n).padStart(2, '0');
            dateInput.value = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
        }
    }

    /**
     * Open the Quick Maintenance Log modal dialog.
     */
    function openMaintenanceModal(defaultAction = 'both') {
        if (!currentMaintenanceData || currentMaintenanceData.has_paired_node === false || !currentMaintenanceData.device_id) {
            showMaintenanceToast('Cannot log maintenance: Probe maintenance (biofilm scrubbing cycle & 2-point pH calibration) requires an active paired pond telemetry node. Please pair a node first.');
            const pairBtn = document.getElementById('btn-open-pair-modal');
            if (pairBtn) pairBtn.click();
            return;
        }

        let modal = document.getElementById('probe-maint-log-modal');
        if (!modal) {
            createLogModalElement();
            modal = document.getElementById('probe-maint-log-modal');
        }
        if (modal) {
            updateLogModalDynamicFields(modal);
            const selectEl = modal.querySelector('#maint-action-select');
            if (selectEl) selectEl.value = defaultAction;

            modal.removeAttribute('hidden');
            modal.classList.add('is-open');
            document.body.classList.add('modal-backdrop-open');
        }
    }

    /**
     * Close the Quick Maintenance Log modal dialog.
     */
    function closeMaintenanceModal() {
        const modal = document.getElementById('probe-maint-log-modal');
        if (modal) {
            modal.classList.remove('is-open');
            modal.setAttribute('hidden', '');
            document.body.classList.remove('modal-backdrop-open');
        }
    }

    /**
     * Open the Maintenance History Modal dialog.
     */
    async function openHistoryModal() {
        let modal = document.getElementById('probe-maint-history-modal');
        if (!modal) {
            createHistoryModalElement();
            modal = document.getElementById('probe-maint-history-modal');
        }
        if (modal) {
            const hasNode = !!(currentMaintenanceData && currentMaintenanceData.has_paired_node);
            const logNewBtn = modal.querySelector('#btn-history-log-new');
            if (logNewBtn) {
                if (!hasNode) {
                    logNewBtn.disabled = true;
                    logNewBtn.classList.add('btn-maint-disabled');
                    logNewBtn.style.opacity = '0.55';
                    logNewBtn.style.cursor = 'not-allowed';
                    logNewBtn.title = 'Pair a pond telemetry node to enable probe maintenance (biofilm scrubbing & 2-point pH calibration)';
                } else {
                    logNewBtn.disabled = false;
                    logNewBtn.classList.remove('btn-maint-disabled');
                    logNewBtn.style.opacity = '1';
                    logNewBtn.style.cursor = 'pointer';
                    logNewBtn.title = 'Log new probe biofilm cleaning or buffer calibration';
                }
            }
            modal.removeAttribute('hidden');
            modal.classList.add('is-open');
            document.body.classList.add('modal-backdrop-open');
            await loadModalHistoryContent();
        }
    }

    /**
     * Close the Maintenance History Modal dialog.
     */
    function closeHistoryModal() {
        const modal = document.getElementById('probe-maint-history-modal');
        if (modal) {
            modal.classList.remove('is-open');
            modal.setAttribute('hidden', '');
            document.body.classList.remove('modal-backdrop-open');
        }
    }

    /**
     * Fetch and load history into the popup history modal.
     */
    async function loadModalHistoryContent() {
        const container = document.getElementById('maint-modal-history-tbody');
        if (!container) return;
        container.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 28px; color: #64748b;">Loading maintenance audit log...</td></tr>';

        const history = await fetchMaintenanceHistory();
        const myEmail = (document.body.dataset.userEmail || (currentMaintenanceData && currentMaintenanceData.user_email) || '').trim().toLowerCase();

        // Strict per-account isolation filter: only show records belonging to the logged-in user
        const userHistory = (history || []).filter((item) => {
            if (!item) return false;
            if (myEmail && item.user_email) {
                return item.user_email.toLowerCase() === myEmail;
            }
            return true;
        });

        if (!userHistory || userHistory.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 32px 20px; color: #64748b;">
                        <div style="font-weight: 600; color: #334155; margin-bottom: 4px;">No Maintenance Logs Recorded Yet</div>
                        <div style="font-size: 13px;">Use the "Log Maintenance" button to record probe cleanings and calibrations once a node is paired.</div>
                    </td>
                </tr>
            `;
            return;
        }

        container.innerHTML = userHistory.map((item) => {
            const badgeClass = item.action === 'both' ? 'maint-badge-both' : (item.action === 'cleaning' ? 'maint-badge-cleaning' : 'maint-badge-calibration');
            const dateStr = item.date_formatted || formatDateTime(item.performed_at);
            const devId = item.device_id || (currentMaintenanceData && currentMaintenanceData.device_id) || 'N/A';
            const tech = item.performed_by || (document.body.dataset.userName || document.body.dataset.userEmail || 'Technician');

            return `
                <tr>
                    <td class="col-date">
                        <strong class="date-text">${dateStr}</strong>
                    </td>
                    <td class="col-node">
                        <span class="maint-chip-node">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                            ${devId}
                        </span>
                    </td>
                    <td class="col-proc">
                        <span class="maint-badge ${badgeClass}">
                            ${item.maintenance_type || 'Routine Maintenance'}
                        </span>
                    </td>
                    <td class="col-tech">
                        <span class="tech-name">${tech}</span>
                    </td>
                    <td class="col-notes">
                        <p class="notes-text">${item.notes || 'Routine cleaning and buffer calibration completed.'}</p>
                    </td>
                    <td class="col-status" style="text-align: center;">
                        <span class="maint-drift-reset-chip">Drift Reset (0d)</span>
                    </td>
                </tr>
            `;
        }).join('');
    }

    /**
     * Submit probe maintenance record to backend.
     */
    async function submitMaintenanceForm(e) {
        e.preventDefault();
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn ? submitBtn.innerHTML : 'Saving...';

        const action = form.action.value;
        const notes = form.notes.value.trim();
        const technician = form.technician.value.trim();
        const deviceId = form.device_id.value || (currentMaintenanceData && currentMaintenanceData.device_id) || '';
        const performedAt = form.performed_at ? form.performed_at.value : '';

        if (!deviceId || !currentMaintenanceData || !currentMaintenanceData.has_paired_node) {
            showMaintenanceToast('Cannot log maintenance: Probe maintenance (biofilm scrubbing cycle & 2-point pH calibration) requires an active paired pond telemetry node. Please pair a node first.');
            return;
        }

        try {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span>Saving Record...</span>';
            }

            const response = await fetch('/api/maintenance/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: action,
                    notes: notes,
                    technician: technician,
                    device_id: deviceId,
                    performed_at: performedAt
                })
            });

            const result = await response.json();
            if (response.ok && result.success) {
                closeMaintenanceModal();
                showMaintenanceToast(result.message || 'Probe maintenance logged and drift schedule reset!');
                await fetchMaintenanceStatus();
                await fetchMaintenanceHistory();

                // If notification system is active, refresh badge & list
                if (typeof window.renderNotifications === 'function') {
                    window.renderNotifications();
                }
            } else {
                alert(result.error || 'Unable to log maintenance. Please retry.');
            }
        } catch (err) {
            console.error('Error logging maintenance:', err);
            alert('Failed to contact server. Please check connection.');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        }
    }

    /**
     * Display a floating success toast.
     */
    function showMaintenanceToast(msg) {
        let toast = document.getElementById('maint-floating-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'maint-floating-toast';
            toast.className = 'maint-toast-notification';
            document.body.appendChild(toast);
        }
        toast.innerHTML = `
            <svg class="ui-icon" style="width: 20px; height: 20px; fill: #10b981;"><use href="#icon-check-circle"></use></svg>
            <span>${msg}</span>
        `;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 4000);
    }

    /**
     * Create the SOP Guide Modal DOM Element.
     */
    function createSOPModalElement() {
        const modalDiv = document.createElement('div');
        modalDiv.id = 'probe-maint-sop-modal';
        modalDiv.className = 'maint-modal-backdrop';
        modalDiv.setAttribute('hidden', '');

        modalDiv.innerHTML = `
            <div class="maint-modal-container" role="dialog" aria-labelledby="sop-modal-title">
                <div class="maint-modal-header">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div class="maint-modal-icon-badge">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                        </div>
                        <div>
                            <span class="maint-modal-eyebrow">BIOFOULING COUNTERMEASURE STANDARD OPERATING PROCEDURE</span>
                            <h2 id="sop-modal-title">Probe Cleaning &amp; 2-Point Recalibration Protocol</h2>
                        </div>
                    </div>
                    <button type="button" class="maint-modal-close" id="btn-close-sop-modal" aria-label="Close modal">
                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-x"></use></svg>
                    </button>
                </div>

                <div class="maint-modal-body">
                    <div class="sop-intro-box">
                        <p>
                            <strong>Scientific Context:</strong> In brackish <em>Penaeus vannamei</em> ponds, microalgae, bacteria, and organic detritus adhere to the glass sensing membrane of the DFRobot pH probe and DS18B20 sleeve within 5–7 days.
                            This microbial biofilm impedes hydronium ion (\\(H^+\\)) exchange across the porous reference junction, causing <strong>electrochemical sensor drift</strong> (false pH readings and sluggish response). Routine scrubbing and buffer recalibration ensure accurate water quality monitoring and early stress detection.
                        </p>
                    </div>

                    <div class="sop-steps-flow">
                        <!-- Step 1 -->
                        <div class="sop-step-card">
                            <div class="sop-step-num">01</div>
                            <div class="sop-step-content">
                                <h3>Safe Pond Extraction &amp; Inspection</h3>
                                <p>
                                    Safely retrieve the paired telemetry node from the pond mounting bracket. Inspect the pH probe glass bulb and reference junction under good lighting. Note visible green algae, brown biofilm slime, or white mineral scaling.
                                </p>
                                <div class="sop-step-tip">
                                    <svg class="ui-icon"><use href="#icon-lightbulb"></use></svg>
                                    <span>Do not touch the delicate glass bulb with bare fingers; skin oils coat the ion-selective membrane.</span>
                                </div>
                            </div>
                        </div>

                        <!-- Step 2 -->
                        <div class="sop-step-card">
                            <div class="sop-step-num">02</div>
                            <div class="sop-step-content">
                                <h3>Biofilm Removal &amp; Deionized Water Rinse</h3>
                                <p>
                                    Immerse the probe tip in clean deionized (DI) or distilled water. Gently brush away the slippery biofilm layer using a soft-bristled nylon camel-hair brush or non-abrasive cotton swab. 
                                    Rinse thoroughly with DI water. If organic residue resists water, soak in neutral laboratory detergent for 3 minutes, then rinse.
                                </p>
                                <div class="sop-step-tip">
                                    <svg class="ui-icon"><use href="#icon-alert"></use></svg>
                                    <span><strong>Never use abrasive pads or rough paper towels:</strong> Micro-scratches permanently degrade the bulb's Nernstian slope.</span>
                                </div>
                            </div>
                        </div>

                        <!-- Step 3 -->
                        <div class="sop-step-card">
                            <div class="sop-step-num">03</div>
                            <div class="sop-step-content">
                                <h3>2-Point Buffer Recalibration (pH 6.86 &amp; 4.01)</h3>
                                <p>
                                    Prepare standard buffer sachets (pH 6.86 neutral midpoint and pH 4.01 acidic slope). Immerse both the pH probe and DS18B20 in pH 6.86 buffer.
                                    Wait 45 seconds for thermal equilibrium. Adjust potentiometer / offset until reading stabilizes at 6.86 (with temp compensation).
                                    Rinse with DI water, blot dry gently with lint-free wipe, and immerse in pH 4.01 buffer to verify slope linearity.
                                </p>
                                <div class="sop-step-tip">
                                    <svg class="ui-icon"><use href="#icon-check-circle"></use></svg>
                                    <span>Optimal tolerance: Readings within &plusmn;0.05 pH of buffer reference values at actual solution temperature.</span>
                                </div>
                            </div>
                        </div>

                        <!-- Step 4 -->
                        <div class="sop-step-card">
                            <div class="sop-step-num">04</div>
                            <div class="sop-step-content">
                                <h3>Re-immersion &amp; Maintenance Logging</h3>
                                <p>
                                    Reinstall probes into the submerged floating rig at 30–50 cm water depth, away from direct aeration churn.
                                    Verify nominal telemetry stream on the local 20x4 LCD and dashboard. Click <strong>"Mark Cleaned &amp; Calibrated"</strong> below to reset the drift monitoring timers.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="maint-modal-footer" style="flex-wrap: wrap; gap: 8px;">
                    <button type="button" class="btn-maint-secondary" id="btn-sop-view-history">
                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-calendar"></use></svg>
                        <span>View History Log</span>
                    </button>
                    <button type="button" class="btn-maint-secondary" id="btn-close-sop-footer">Close Guide</button>
                    <button type="button" class="btn-maint-primary" id="btn-sop-proceed-log">
                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>
                        <span>Proceed to Log Maintenance</span>
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modalDiv);

        modalDiv.querySelector('#btn-close-sop-modal').addEventListener('click', closeSOPModal);
        modalDiv.querySelector('#btn-close-sop-footer').addEventListener('click', closeSOPModal);
        modalDiv.querySelector('#btn-sop-view-history').addEventListener('click', () => {
            closeSOPModal();
            openHistoryModal();
        });
        modalDiv.querySelector('#btn-sop-proceed-log').addEventListener('click', (e) => {
            if (!currentMaintenanceData || !currentMaintenanceData.has_paired_node) {
                e.preventDefault();
                showMaintenanceToast('Cannot log maintenance: Probe maintenance (biofilm scrubbing cycle & 2-point pH calibration) requires an active paired pond telemetry node. Please pair a node first.');
                closeSOPModal();
                const pairBtn = document.getElementById('btn-open-pair-modal');
                if (pairBtn) pairBtn.click();
                return;
            }
            closeSOPModal();
            openMaintenanceModal('both');
        });

        modalDiv.addEventListener('click', (e) => {
            if (e.target === modalDiv) closeSOPModal();
        });
    }

    /**
     * Create the Quick Log Modal DOM Element.
     */
    function createLogModalElement() {
        const modalDiv = document.createElement('div');
        modalDiv.id = 'probe-maint-log-modal';
        modalDiv.className = 'maint-modal-backdrop';
        modalDiv.setAttribute('hidden', '');

        const userEmail = (document.body.dataset.userEmail || (currentMaintenanceData && currentMaintenanceData.user_email) || '').trim();
        const userName = (document.body.dataset.userName || '').trim();
        const defaultTech = userName || userEmail || 'Pond Operator';
        const activeNodeId = (currentMaintenanceData && currentMaintenanceData.has_paired_node && currentMaintenanceData.device_id)
            ? currentMaintenanceData.device_id
            : '';
        const displayNodeBadge = activeNodeId || 'No Paired Node';

        modalDiv.innerHTML = `
            <div class="maint-modal-container maint-modal-sm maint-log-dialog" role="dialog" aria-labelledby="log-modal-title" aria-modal="true">
                <form id="probe-maint-form" class="maint-form-wrapper">
                    <input type="hidden" name="device_id" value="${activeNodeId}">

                    <div class="maint-modal-header">
                        <div class="maint-header-info-wrap">
                            <div class="maint-modal-icon-badge">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>
                            </div>
                            <div>
                                <span class="maint-modal-eyebrow">SENSOR HEALTH &amp; ANTI-DRIFT RECORD</span>
                                <h2 id="log-modal-title">Log Probe Maintenance &amp; Reset Timer</h2>
                                <p class="maint-modal-subtitle">Record cleaning or calibration to clear drift alerts and reset telemetry countdowns</p>
                            </div>
                        </div>
                        <button type="button" class="maint-modal-close" id="btn-close-log-modal" aria-label="Close dialog">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-x"></use></svg>
                        </button>
                    </div>

                    <div class="maint-modal-body">
                        <!-- Target Hardware Node Summary Card -->
                        <div class="maint-target-context-card">
                            <div class="maint-target-context-icon">
                                <svg class="ui-icon" aria-hidden="true"><use href="#icon-activity"></use></svg>
                            </div>
                            <div class="maint-target-context-info">
                                <div class="maint-target-context-title">
                                    <strong>Node Submerged Probes</strong>
                                    <span class="maint-target-id-badge">${displayNodeBadge}</span>
                                </div>
                                <p class="maint-target-context-sub">DFRobot Industrial pH Sensor &amp; DS18B20 Digital Temperature</p>
                            </div>
                            <div class="maint-target-context-chip">
                                <span class="status-pulse-dot" style="background: #10b981;"></span>
                                <span>Active Probe</span>
                            </div>
                        </div>

                        <div class="maint-form-fields-grid">
                            <!-- Maintenance Procedure -->
                            <div class="maint-form-field">
                                <label for="maint-action-select" class="maint-label">
                                    <svg class="ui-icon label-icon" aria-hidden="true"><use href="#icon-settings"></use></svg>
                                    <span>Maintenance Procedure Performed *</span>
                                </label>
                                <div class="maint-select-wrapper">
                                    <select id="maint-action-select" name="action" class="maint-select" required>
                                        <option value="both" selected>Full Protocol: Biofilm Scrubbing &amp; 2-Point pH Recalibration</option>
                                        <option value="cleaning">Routine Biofilm Scrubbing &amp; DI Rinse Only (7-Day Cycle)</option>
                                        <option value="calibration">2-Point pH Buffer Recalibration Only (14-Day Cycle)</option>
                                    </select>
                                    <svg class="ui-icon maint-select-chevron" aria-hidden="true"><use href="#icon-arrow"></use></svg>
                                </div>
                                <span class="maint-hint">Resetting will update the operational countdown and clear biofilm drift warnings.</span>
                            </div>

                            <!-- Row for Technician and Date/Time -->
                            <div class="maint-form-row">
                                <div class="maint-form-field">
                                    <label for="maint-technician-input" class="maint-label">
                                        <svg class="ui-icon label-icon" aria-hidden="true"><use href="#icon-user"></use></svg>
                                        <span>Technician / Operator *</span>
                                    </label>
                                    <input type="text" id="maint-technician-input" name="technician" class="maint-input" value="${defaultTech}" placeholder="e.g. Pond Operator" required>
                                </div>

                                <div class="maint-form-field">
                                    <label for="maint-datetime-input" class="maint-label">
                                        <svg class="ui-icon label-icon" aria-hidden="true"><use href="#icon-clock"></use></svg>
                                        <span>Date &amp; Time *</span>
                                    </label>
                                    <input type="datetime-local" id="maint-datetime-input" name="performed_at" class="maint-input" required>
                                </div>
                            </div>

                            <!-- Calibration Notes -->
                            <div class="maint-form-field">
                                <label for="maint-notes-input" class="maint-label">
                                    <svg class="ui-icon label-icon" aria-hidden="true"><use href="#icon-message"></use></svg>
                                    <span>Calibration Notes &amp; Buffer Offsets (Optional)</span>
                                </label>
                                <textarea id="maint-notes-input" name="notes" class="maint-textarea" rows="3" placeholder="e.g. Gently cleaned algal biofilm with soft camel-hair brush; 2-point verified with pH 6.86 and 4.01 standard buffers at 29.5°C. Voltage offset verified."></textarea>
                                <span class="maint-hint">All entries are permanently logged in the maintenance audit trail for quality assurance.</span>
                            </div>
                        </div>
                    </div>

                    <div class="maint-modal-footer">
                        <button type="button" class="btn-maint-secondary" id="btn-cancel-log-modal">Cancel</button>
                        <button type="submit" class="btn-maint-primary" id="btn-submit-maint-form">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>
                            <span>Save &amp; Reset Maintenance Timers</span>
                        </button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modalDiv);

        modalDiv.querySelector('#btn-close-log-modal').addEventListener('click', closeMaintenanceModal);
        modalDiv.querySelector('#btn-cancel-log-modal').addEventListener('click', closeMaintenanceModal);
        modalDiv.querySelector('#probe-maint-form').addEventListener('submit', submitMaintenanceForm);
        modalDiv.addEventListener('click', (e) => {
            if (e.target === modalDiv) closeMaintenanceModal();
        });
    }

    /**
     * Create the Full Maintenance History Modal DOM Element.
     */
    function createHistoryModalElement() {
        const modalDiv = document.createElement('div');
        modalDiv.id = 'probe-maint-history-modal';
        modalDiv.className = 'maint-modal-backdrop';
        modalDiv.setAttribute('hidden', '');

        modalDiv.innerHTML = `
            <div class="maint-modal-container maint-modal-history-container" role="dialog" aria-labelledby="history-modal-title">
                <div class="maint-modal-header">
                    <div class="maint-header-info-wrap">
                        <div class="maint-modal-icon-badge" style="background: #f0fdf4; color: #126b4f;">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-calendar"></use></svg>
                        </div>
                        <div>
                            <span class="maint-modal-eyebrow">AUDIT &amp; QUALITY ASSURANCE LOG</span>
                            <h2 id="history-modal-title">Probe Maintenance &amp; Calibration Audit Log</h2>
                        </div>
                    </div>
                    <button type="button" class="maint-modal-close" id="btn-close-history-modal" aria-label="Close modal">
                        <svg class="ui-icon" aria-hidden="true"><use href="#icon-x"></use></svg>
                    </button>
                </div>

                <div class="maint-modal-body" style="padding: 18px 24px;">
                    <div class="maint-history-table-wrapper">
                        <table class="maint-history-table">
                            <thead>
                                <tr>
                                    <th style="width: 160px; min-width: 150px;">Date &amp; Time</th>
                                    <th style="width: 90px; min-width: 85px;">Node</th>
                                    <th style="width: 180px; min-width: 170px;">Procedure</th>
                                    <th style="width: 120px; min-width: 110px;">Technician</th>
                                    <th style="min-width: 240px;">Notes &amp; Buffer Offsets</th>
                                    <th style="width: 110px; min-width: 100px; text-align: center;">Drift Status</th>
                                </tr>
                            </thead>
                            <tbody id="maint-modal-history-tbody">
                                <tr>
                                    <td colspan="6" style="text-align: center; padding: 28px; color: #64748b;">
                                        Loading probe maintenance audit log...
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="maint-modal-footer" style="justify-content: space-between;">
                    <span style="font-size: 12px; color: #64748b;">All maintenance events are permanently audited for quality assurance.</span>
                    <div style="display: flex; gap: 8px;">
                        <button type="button" class="btn-maint-secondary" id="btn-close-history-footer">Close</button>
                        <button type="button" class="btn-maint-primary" id="btn-history-log-new">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-plus"></use></svg>
                            <span>Log New Maintenance</span>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modalDiv);

        modalDiv.querySelector('#btn-close-history-modal').addEventListener('click', closeHistoryModal);
        modalDiv.querySelector('#btn-close-history-footer').addEventListener('click', closeHistoryModal);
        modalDiv.querySelector('#btn-history-log-new').addEventListener('click', (e) => {
            if (!currentMaintenanceData || !currentMaintenanceData.has_paired_node) {
                e.preventDefault();
                showMaintenanceToast('Cannot log maintenance: Probe maintenance (biofilm scrubbing cycle & 2-point pH calibration) requires an active paired pond telemetry node. Please pair a node first.');
                closeHistoryModal();
                const pairBtn = document.getElementById('btn-open-pair-modal');
                if (pairBtn) pairBtn.click();
                return;
            }
            closeHistoryModal();
            openMaintenanceModal('both');
        });
        modalDiv.addEventListener('click', (e) => {
            if (e.target === modalDiv) closeHistoryModal();
        });
    }

    // Expose helpers globally for cross-module integration
    window.ShrimpGuardMaintenance = {
        fetchStatus: fetchMaintenanceStatus,
        fetchHistory: fetchMaintenanceHistory,
        openSOPModal: openSOPModal,
        openLogModal: openMaintenanceModal,
        openHistoryModal: openHistoryModal,
        closeSOPModal: closeSOPModal,
        closeLogModal: closeMaintenanceModal,
        closeHistoryModal: closeHistoryModal
    };

    // Global delegated click handler for maintenance actions
    document.addEventListener('click', (e) => {
        const sopBtn = e.target.closest('#btn-devices-open-sop, #btn-open-sop-modal');
        if (sopBtn) {
            e.preventDefault();
            openSOPModal();
            return;
        }

        const histBtn = e.target.closest('#btn-devices-view-history, #btn-open-history-modal');
        if (histBtn) {
            e.preventDefault();
            openHistoryModal();
            return;
        }

        const logBtn = e.target.closest('#btn-devices-log-maint, #btn-open-log-modal');
        if (logBtn) {
            e.preventDefault();
            if (!currentMaintenanceData || !currentMaintenanceData.has_paired_node) {
                showMaintenanceToast('Cannot log maintenance: Probe maintenance (biofilm scrubbing cycle & 2-point pH calibration) requires an active paired pond telemetry node. Please pair a node first.');
                const pairBtn = document.getElementById('btn-open-pair-modal');
                if (pairBtn) pairBtn.click();
                return;
            }
            openMaintenanceModal('both');
            return;
        }
    });

    function initMaintenanceEngine() {
        const preLogBtn = document.getElementById('btn-devices-log-maint');
        if (preLogBtn) {
            preLogBtn.addEventListener('click', (e) => {
                if (!currentMaintenanceData || !currentMaintenanceData.has_paired_node) {
                    e.preventDefault();
                    showMaintenanceToast('Cannot log maintenance: Probe maintenance (biofilm scrubbing cycle & 2-point pH calibration) requires an active paired pond telemetry node. Please pair a node first.');
                    const pairBtn = document.getElementById('btn-open-pair-modal');
                    if (pairBtn) pairBtn.click();
                    return;
                }
                openMaintenanceModal('both');
            });
        }
        const preSopBtn = document.getElementById('btn-devices-open-sop');
        if (preSopBtn) preSopBtn.addEventListener('click', () => openSOPModal());
        const preHistBtn = document.getElementById('btn-devices-view-history');
        if (preHistBtn) preHistBtn.addEventListener('click', () => openHistoryModal());

        fetchMaintenanceStatus();
        fetchMaintenanceHistory();

        // Periodic background poll every 60 seconds
        setInterval(fetchMaintenanceStatus, 60000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMaintenanceEngine);
    } else {
        initMaintenanceEngine();
    }

})();
