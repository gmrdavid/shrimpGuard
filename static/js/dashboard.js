function parseSafeDate(val) {
    if (!val) return null;
    if (val instanceof Date) return isNaN(val.getTime()) ? null : val;
    const s = String(val).trim();
    let d = new Date(s);
    if (!isNaN(d.getTime())) return d;
    d = new Date(s.replace(" ", "T"));
    if (!isNaN(d.getTime())) return d;
    return null;
}

function displayResults(data) {
    const tempNum = Number(data.temperature);
    const phNum = Number(data.ph);
    const isSensorFault = tempNum <= -120 || Boolean(data.is_sensor_fault);

    // Temperature display with sensor disconnect safeguard
    const tempEl = document.getElementById("temperature");
    if (tempEl) {
        if (isSensorFault) {
            tempEl.textContent = "ERR (-127)";
            tempEl.title = "DS18B20 1-Wire sensor disconnected in pond";
        } else {
            tempEl.textContent = !isNaN(tempNum) ? tempNum.toFixed(2) : data.temperature;
            tempEl.title = "Live temperature from pond DS18B20 sensor";
        }
    }

    // pH display
    const phEl = document.getElementById("ph");
    if (phEl) {
        phEl.textContent = !isNaN(phNum) ? phNum.toFixed(2) : data.ph;
        phEl.title = "Live pH from pond DFRobot sensor";
    }

    // Per-parameter status strictly derived from the DecisionTreeClassifier ML model
    let tempStatus = data.temperature_status || (data.status === "Critical" ? "Critical" : (data.status === "Warning" ? "Warning" : "Optimal"));
    if (isSensorFault) {
        tempStatus = "Sensor Disconnected";
    }
    const phStatus = data.ph_status || (data.status === "Critical" ? "Critical" : (data.status === "Warning" ? "Warning" : "Optimal"));

    const tempStatusEl = document.getElementById("temperature-status");
    if (tempStatusEl) {
        tempStatusEl.textContent = tempStatus;
        tempStatusEl.className = isSensorFault
            ? "metric-status status-critical"
            : `metric-status status-${tempStatus.toLowerCase().replace(/[^a-z]/g, "")}`;
    }

    const phStatusEl = document.getElementById("ph-status");
    if (phStatusEl) {
        phStatusEl.textContent = phStatus;
        phStatusEl.className = `metric-status status-${phStatus.toLowerCase().replace(/[^a-z]/g, "")}`;
    }

    // Update telemetry header indicators
    const recDate = parseSafeDate(data.recorded_at);
    const now = new Date();
    const secondsAgo = recDate ? Math.max(0, Math.floor((now - recDate) / 1000)) : 999;

    const streamBadge = document.getElementById("telemetry-stream-badge");
    const streamBadgeText = document.getElementById("telemetry-badge-text");
    if (streamBadge && streamBadgeText) {
        if (data.is_connected || secondsAgo <= 25) {
            streamBadge.className = "telemetry-live-badge badge-active";
            const portName = data.connected_port ? ` (${data.connected_port})` : "";
            streamBadgeText.textContent = `RECEIVING SENSOR DATA${portName}`;
            const dot = streamBadge.querySelector(".status-indicator-dot");
            if (dot) dot.className = "status-indicator-dot dot-optimal";
        } else {
            streamBadge.className = "telemetry-live-badge badge-waiting";
            streamBadgeText.textContent = "WAITING FOR TRANSMISSION";
            const dot = streamBadge.querySelector(".status-indicator-dot");
            if (dot) dot.className = "status-indicator-dot dot-warning";
        }
    }

    const lastSyncEl = document.getElementById("telemetry-last-sync");
    if (lastSyncEl) {
        lastSyncEl.textContent = recDate && !isNaN(recDate.getTime())
            ? recDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
            : "Listening...";
    }

    const secAgoEl = document.getElementById("telemetry-seconds-ago");
    if (secAgoEl) {
        secAgoEl.textContent = secondsAgo < 5
            ? "Just now (streaming live)"
            : (secondsAgo < 60 ? `${secondsAgo}s ago` : `${Math.floor(secondsAgo / 60)}m ago`);
    }

    const nodeEl = document.getElementById("telemetry-node-id");
    if (nodeEl) {
        nodeEl.textContent = data.device_id || "NODE01";
    }

    const mlBadgeEl = document.getElementById("telemetry-ml-badge");
    if (mlBadgeEl) {
        const overall = data.status || "Optimal";
        mlBadgeEl.textContent = overall.toUpperCase();
        mlBadgeEl.style.color = overall === "Optimal" ? "#126b4f" : (overall === "Warning" ? "#d97706" : "#dc2626");
    }

    const lastUpdEl = document.getElementById("last-updated");
    if (lastUpdEl) {
        lastUpdEl.textContent = recDate && !isNaN(recDate.getTime())
            ? `Last updated ${recDate.toLocaleString()}`
            : "";
    }
    document.getElementById("dashboard-demo-note").hidden = data.status !== "Demo";
    updateStatus(data);
    calculateWQI(data);
    createAlerts(data);
}


async function saveReading(data) {
    const reading = {
        ...data,
        recorded_at: new Date().toISOString()
    };

    const response = await fetch("/api/readings", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(reading)
    });

    if (!response.ok) {
        const result = await response.json();
        throw new Error(result.error || "Unable to save reading to the database.");
    }

    return response.json();
}


function updateDeviceTime() {
    const timeEl = document.getElementById("time");
    if (timeEl) {
        timeEl.textContent =
            new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    }
}


function updateGreeting() {
    const greetingEl = document.getElementById("dashboard-greeting");
    if (!greetingEl) return;
    const hour = new Date().getHours();
    let timeGreeting = "Good evening";
    if (hour >= 5 && hour < 12) {
        timeGreeting = "Good morning";
    } else if (hour >= 12 && hour < 18) {
        timeGreeting = "Good afternoon";
    }
    const userName = greetingEl.dataset.userName || "Grower";
    greetingEl.textContent = `${timeGreeting}, ${userName}!`;
}


function updateStatus(data) {
    const rawStatus = (data && data.status) ? String(data.status).trim() : "";
    let classification = "Optimal";

    if (rawStatus.toLowerCase().includes("critical")) {
        classification = "Critical";
    } else if (rawStatus.toLowerCase().includes("warning")) {
        classification = "Warning";
    } else if (rawStatus.toLowerCase().includes("optimal") || rawStatus.toLowerCase().includes("normal") || rawStatus.toLowerCase().includes("good")) {
        classification = "Optimal";
    }

    const overallStatusEl = document.getElementById("overall-status");
    if (overallStatusEl) {
        overallStatusEl.textContent = classification;
        overallStatusEl.className = `status-heading status-${classification.toLowerCase()}`;
    }

    const indicatorDot = document.querySelector(".status-indicator-dot");
    if (indicatorDot) {
        indicatorDot.className = `status-indicator-dot dot-${classification.toLowerCase()}`;
    }
}


function calculateWQI(data) {
    if (!data) return;

    // 1. Direct ML Analysis rendering if pre-calculated by backend
    if (data.temp_adjustment && data.ph_adjustment && data.wqi_score !== undefined) {
        const accuracyScore = Number(data.wqi_score);
        const wqiValueEl = document.getElementById("wqi-value");
        if (wqiValueEl) wqiValueEl.textContent = `${accuracyScore}%`;

        const statusLabel = data.wqi_status || (accuracyScore >= 90 ? "OPTIMAL QUALITY" : (accuracyScore >= 70 ? "WARNING CONDITION" : "CRITICAL CONDITION"));
        const statusTheme = data.wqi_theme || (accuracyScore >= 90 ? "optimal" : (accuracyScore >= 70 ? "warning" : "critical"));

        const wqiStatusEl = document.getElementById("wqi-status");
        if (wqiStatusEl) {
            wqiStatusEl.textContent = statusLabel;
            wqiStatusEl.className = `wqi-status-heading status-${statusTheme}`;
        }

        const tempAdj = data.temp_adjustment;
        const tempPercentEl = document.getElementById("temp-norm-percent");
        if (tempPercentEl) tempPercentEl.textContent = tempAdj.percent_text || "0.0%";
        const tempBadgeEl = document.getElementById("temp-norm-badge");
        if (tempBadgeEl) {
            tempBadgeEl.textContent = tempAdj.badge_text || "Normal";
            tempBadgeEl.className = `wqi-metric-badge ${tempAdj.badge_class || "badge-normal"}`;
        }
        const tempDetailEl = document.getElementById("temp-norm-detail");
        if (tempDetailEl) tempDetailEl.textContent = tempAdj.detail_text;

        const phAdj = data.ph_adjustment;
        const phPercentEl = document.getElementById("ph-norm-percent");
        if (phPercentEl) phPercentEl.textContent = phAdj.percent_text || "0.0%";
        const phBadgeEl = document.getElementById("ph-norm-badge");
        if (phBadgeEl) {
            phBadgeEl.textContent = phAdj.badge_text || "Normal";
            phBadgeEl.className = `wqi-metric-badge ${phAdj.badge_class || "badge-normal"}`;
        }
        const phDetailEl = document.getElementById("ph-norm-detail");
        if (phDetailEl) phDetailEl.textContent = phAdj.detail_text;

        const accuracyPercentEl = document.getElementById("wqi-accuracy-percent");
        if (accuracyPercentEl) accuracyPercentEl.textContent = `${accuracyScore}%`;
        const accuracyBadgeEl = document.getElementById("wqi-accuracy-badge");
        if (accuracyBadgeEl) {
            accuracyBadgeEl.textContent = statusLabel;
            accuracyBadgeEl.className = `wqi-metric-badge badge-${statusTheme}`;
        }
        return;
    }

    // 2. Dynamic ML model evaluation fallback
    const temp = Number(data.temperature);
    const ph = Number(data.ph);
    if (isNaN(temp) || isNaN(ph)) return;

    const tempMin = 28.0;
    const tempMax = 32.0;
    const phMin = 7.50;
    const phMax = 8.50;

    let tempStatus = "Optimal";
    if (temp <= 25.01 || temp > 33.50) tempStatus = "Critical";
    else if (temp < tempMin || temp > tempMax) tempStatus = "Warning";

    let phStatus = "Optimal";
    if (ph <= 6.49 || ph > 9.01) phStatus = "Critical";
    else if (ph < phMin || ph > phMax) phStatus = "Warning";

    let overallStatus = "Optimal";
    if (tempStatus === "Critical" || phStatus === "Critical") overallStatus = "Critical";
    else if (tempStatus === "Warning" || phStatus === "Warning") overallStatus = "Warning";

    let tempDiffPercent = 0.0;
    let tempBadgeText = "Normal";
    let tempBadgeClass = "badge-normal";
    let tempDetailText = `Current: ${temp.toFixed(2)} °C · Within ML optimal range (28.00–32.00 °C)`;

    if (temp < tempMin) {
        const diff = tempMin - temp;
        tempDiffPercent = (diff / temp) * 100;
        tempBadgeText = `+${tempDiffPercent.toFixed(1)}% Needed`;
        tempBadgeClass = tempStatus === "Critical" ? "badge-critical" : "badge-warning";
        tempDetailText = `Increase by +${diff.toFixed(2)} °C to reach ML optimal range (28.00–32.00 °C)`;
    } else if (temp > tempMax) {
        const diff = temp - tempMax;
        tempDiffPercent = (diff / temp) * 100;
        tempBadgeText = `-${tempDiffPercent.toFixed(1)}% Needed`;
        tempBadgeClass = tempStatus === "Critical" ? "badge-critical" : "badge-warning";
        tempDetailText = `Decrease by -${diff.toFixed(2)} °C to reach ML optimal range (28.00–32.00 °C)`;
    }

    const tempPercentEl = document.getElementById("temp-norm-percent");
    if (tempPercentEl) tempPercentEl.textContent = tempDiffPercent === 0 ? "0.0%" : (temp < tempMin ? `+${tempDiffPercent.toFixed(1)}%` : `-${tempDiffPercent.toFixed(1)}%`);
    const tempBadgeEl = document.getElementById("temp-norm-badge");
    if (tempBadgeEl) {
        tempBadgeEl.textContent = tempBadgeText;
        tempBadgeEl.className = `wqi-metric-badge ${tempBadgeClass}`;
    }
    const tempDetailEl = document.getElementById("temp-norm-detail");
    if (tempDetailEl) tempDetailEl.textContent = tempDetailText;

    let phDiffPercent = 0.0;
    let phBadgeText = "Normal";
    let phBadgeClass = "badge-normal";
    let phDetailText = `Current: ${ph.toFixed(2)} · Within ML optimal range (7.50–8.50)`;

    if (ph < phMin) {
        const diff = phMin - ph;
        phDiffPercent = (diff / ph) * 100;
        phBadgeText = `+${phDiffPercent.toFixed(1)}% Needed`;
        phBadgeClass = phStatus === "Critical" ? "badge-critical" : "badge-warning";
        phDetailText = `Increase by +${diff.toFixed(2)} to reach ML optimal range (7.50–8.50)`;
    } else if (ph > phMax) {
        const diff = ph - phMax;
        phDiffPercent = (diff / ph) * 100;
        phBadgeText = `-${phDiffPercent.toFixed(1)}% Needed`;
        phBadgeClass = phStatus === "Critical" ? "badge-critical" : "badge-warning";
        phDetailText = `Decrease by -${diff.toFixed(2)} to reach ML optimal range (7.50–8.50)`;
    }

    const phPercentEl = document.getElementById("ph-norm-percent");
    if (phPercentEl) phPercentEl.textContent = phDiffPercent === 0 ? "0.0%" : (ph < phMin ? `+${phDiffPercent.toFixed(1)}%` : `-${phDiffPercent.toFixed(1)}%`);
    const phBadgeEl = document.getElementById("ph-norm-badge");
    if (phBadgeEl) {
        phBadgeEl.textContent = phBadgeText;
        phBadgeEl.className = `wqi-metric-badge ${phBadgeClass}`;
    }
    const phDetailEl = document.getElementById("ph-norm-detail");
    if (phDetailEl) phDetailEl.textContent = phDetailText;

    let wqiScore = 100;
    if (overallStatus === "Optimal") {
        const tPen = Math.min(5, (Math.abs(temp - 30.0) / 2.0) * 5);
        const pPen = Math.min(5, (Math.abs(ph - 8.0) / 0.5) * 5);
        wqiScore = Math.max(90, Math.min(100, Math.round(100 - tPen - pPen)));
    } else if (overallStatus === "Warning") {
        const tPen = tempStatus === "Warning" ? 12 : 0;
        const pPen = phStatus === "Warning" ? 12 : 0;
        wqiScore = Math.max(70, Math.min(89, Math.round(100 - tPen - pPen)));
    } else {
        const tPen = tempStatus === "Critical" ? 25 : (tempStatus === "Warning" ? 12 : 0);
        const pPen = phStatus === "Critical" ? 25 : (phStatus === "Warning" ? 12 : 0);
        wqiScore = Math.min(69, Math.max(0, Math.round(100 - tPen - pPen)));
    }

    const wqiValueEl = document.getElementById("wqi-value");
    if (wqiValueEl) wqiValueEl.textContent = `${wqiScore}%`;

    const statusLabel = overallStatus === "Optimal" ? "OPTIMAL QUALITY" : (overallStatus === "Warning" ? "WARNING CONDITION" : "CRITICAL CONDITION");
    const statusTheme = overallStatus.toLowerCase();

    const wqiStatusEl = document.getElementById("wqi-status");
    if (wqiStatusEl) {
        wqiStatusEl.textContent = statusLabel;
        wqiStatusEl.className = `wqi-status-heading status-${statusTheme}`;
    }

    const accuracyPercentEl = document.getElementById("wqi-accuracy-percent");
    if (accuracyPercentEl) accuracyPercentEl.textContent = `${wqiScore}%`;
    const accuracyBadgeEl = document.getElementById("wqi-accuracy-badge");
    if (accuracyBadgeEl) {
        accuracyBadgeEl.textContent = statusLabel;
        accuracyBadgeEl.className = `wqi-metric-badge badge-${statusTheme}`;
    }
}

function createAlerts(data) {
    const alerts = document.getElementById("alerts");
    if (!alerts) return;

    alerts.innerHTML = "";

    const status = (data && data.status) ? data.status : "Optimal";
    const temp = Number(data.temperature);
    const ph = Number(data.ph);

    // Normal / Optimal status determined by ML model
    if (status === "Optimal" || (status !== "Critical" && status !== "Warning" && temp >= 28 && temp <= 32 && ph >= 7.5 && ph <= 8.5)) {
        alerts.innerHTML = `
            <div class="status-box">
                <svg class="ui-icon"><use href="#icon-check-circle"></use></svg> No abnormal readings detected. Alerts and notifications are normal.
            </div>
        `;
        return;
    }

    const alertItems = [];
    const severity = status === "Critical" ? "Critical" : "Warning";
    const tempAbnormal = temp < 28.0 || temp > 32.0;
    const phAbnormal = ph < 7.50 || ph > 8.50;

    if (tempAbnormal && phAbnormal) {
        alertItems.push({
            severity,
            title: `${severity} Combined Water Quality Alert`,
            message: `ML model detected ${severity} condition: Water temperature is ${temp.toFixed(2)} °C (optimal: 28.00–32.00 °C) and pH is ${ph.toFixed(2)} (optimal: 7.50–8.50).`,
            notification: `Push: [${severity.toUpperCase()}] Temp ${temp.toFixed(2)}°C, pH ${ph.toFixed(2)}. Immediate pond remediation required.`
        });
    } else if (tempAbnormal) {
        alertItems.push({
            severity,
            title: `${severity} Temperature Alert`,
            message: `ML model detected ${severity} temperature: Currently ${temp.toFixed(2)} °C, outside optimal range of 28.00–32.00 °C.`,
            notification: `Push: [${severity.toUpperCase()}] Pond temperature is ${temp.toFixed(2)}°C. Check cooling/heating systems.`
        });
    } else if (phAbnormal) {
        alertItems.push({
            severity,
            title: `${severity} pH Alert`,
            message: `ML model detected ${severity} pH level: Currently ${ph.toFixed(2)}, outside optimal range of 7.50–8.50.`,
            notification: `Push: [${severity.toUpperCase()}] Pond pH is ${ph.toFixed(2)}. Adjust water buffering and treatment.`
        });
    } else {
        alertItems.push({
            severity,
            title: `${severity} Water Quality Alert`,
            message: `ML model classified pond condition as ${severity} based on current readings (Temp: ${temp.toFixed(2)} °C, pH: ${ph.toFixed(2)}).`,
            notification: `Push: [${severity.toUpperCase()}] Water quality alert generated by ML model.`
        });
    }

    alertItems.forEach((item) => {
        alerts.innerHTML += `
            <div class="alert">
                <svg class="ui-icon"><use href="${item.severity === "Critical" ? "#icon-alert" : "#icon-bell"}"></use></svg> ${item.title}
                <br>
                ${item.message}
                <br><br>
                <strong>Notification:</strong> ${item.notification}
            </div>
        `;
    });
}

updateDeviceTime();
setInterval(updateDeviceTime, 1000);


// --- Automated Live Telemetry Polling & Controls ---
async function loadLatestReading() {
    try {
        const response = await fetch("/api/readings/latest");
        if (!response.ok) {
            throw new Error(`Sensor request failed with status ${response.status}.`);
        }
        const reading = await response.json();
        if (reading) {
            displayResults(reading);
        } else {
            const overallStatusEl = document.getElementById("overall-status");
            if (overallStatusEl) overallStatusEl.textContent = "Awaiting first sensor transmission from pond...";
            const lastSyncEl = document.getElementById("telemetry-last-sync");
            if (lastSyncEl) lastSyncEl.textContent = "Awaiting Node 1";
            const tempEl = document.getElementById("temperature");
            if (tempEl) tempEl.textContent = "--";
            const phEl = document.getElementById("ph");
            if (phEl) phEl.textContent = "--";
            const tempStatusEl = document.getElementById("temperature-status");
            if (tempStatusEl) {
                tempStatusEl.textContent = "No data";
                tempStatusEl.className = "metric-status";
            }
            const phStatusEl = document.getElementById("ph-status");
            if (phStatusEl) {
                phStatusEl.textContent = "No data";
                phStatusEl.className = "metric-status";
            }
        }
    } catch (error) {
        console.error("Unable to load the latest sensor reading:", error);
        const lastSyncEl = document.getElementById("telemetry-last-sync");
        if (lastSyncEl) lastSyncEl.textContent = "Offline";
    }
}

// Sync Now Button
const syncNowBtn = document.getElementById("sync-now-btn");
if (syncNowBtn) {
    syncNowBtn.addEventListener("click", async () => {
        syncNowBtn.disabled = true;
        const origText = syncNowBtn.innerHTML;
        syncNowBtn.innerHTML = `
            <svg class="ui-icon ui-spin" aria-hidden="true"><use href="#icon-activity"></use></svg>
            <span>Syncing...</span>
        `;
        try {
            await loadLatestReading();
        } finally {
            setTimeout(() => {
                syncNowBtn.innerHTML = origText;
                syncNowBtn.disabled = false;
            }, 600);
        }
    });
}

// Test Reading Modal Handlers (For Offline / Lab Simulation)
const testModal = document.getElementById("test-sensor-modal");
const openTestBtn = document.getElementById("open-test-modal-btn");
const closeTestBtn = document.getElementById("close-test-modal-btn");
const cancelTestBtn = document.getElementById("cancel-test-btn");

if (openTestBtn && testModal) {
    openTestBtn.addEventListener("click", () => {
        testModal.hidden = false;
    });
}

function closeTestModal() {
    if (testModal) testModal.hidden = true;
}

if (closeTestBtn) closeTestBtn.addEventListener("click", closeTestModal);
if (cancelTestBtn) cancelTestBtn.addEventListener("click", closeTestModal);

// Quality Form Handler inside Test Modal
const qualityForm = document.getElementById("quality-form");
if (qualityForm) {
    qualityForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData(event.currentTarget);
        const data = {
            temperature: Number(formData.get("temperature")),
            ph: Number(formData.get("ph")),
            device_id: "SIM-NODE01"
        };

        const submitButton = event.currentTarget.querySelector("button[type=submit]");
        if (submitButton) submitButton.disabled = true;
        try {
            const savedReading = await saveReading(data);
            displayResults(savedReading);
            closeTestModal();
            window.dispatchEvent(new Event('shrimpguard:notification-update'));
        } catch (error) {
            console.error("Unable to save simulated water quality reading:", error);
            window.alert(`Unable to ingest test reading: ${error.message}`);
        } finally {
            if (submitButton) submitButton.disabled = false;
        }
    });
}

// Also intercept sensor fault in createAlerts
const origCreateAlerts = createAlerts;
createAlerts = function(data) {
    origCreateAlerts(data);
    const alertsEl = document.getElementById("alerts");
    if (!alertsEl || !data) return;

    const tempNum = Number(data.temperature);
    if (tempNum <= -120 || Boolean(data.is_sensor_fault)) {
        const faultHtml = `
            <div class="alert alert-sensor-fault" style="border-left: 4px solid #dc2626; background: #fef2f2; padding: 12px 14px; margin-bottom: 12px; border-radius: 8px;">
                <strong style="color: #991b1b; display: flex; align-items: center; gap: 6px;">
                    <svg class="ui-icon" style="width: 18px; height: 18px; stroke: #dc2626;"><use href="#icon-alert"></use></svg>
                    CRITICAL: DS18B20 Temperature Sensor Disconnected (-127 °C)
                </strong>
                <p style="margin: 6px 0 0; color: #7f1d1d; font-size: 13px;">
                    Node 1 in the pond reported a sensor disconnection code. Verify the waterproof probe cable and 4.7kΩ pull-up resistor on GPIO 4.
                </p>
            </div>
        `;
        alertsEl.innerHTML = faultHtml + alertsEl.innerHTML;
    }
};

// Entrypoint initialization
updateDeviceTime();
setInterval(updateDeviceTime, 1000);
updateGreeting();
setInterval(updateGreeting, 60000);

// Poll live sensor telemetry every 4 seconds (Node 1 transmits every 5 seconds)
loadLatestReading();
setInterval(loadLatestReading, 4000);
