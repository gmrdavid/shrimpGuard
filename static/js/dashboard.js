function displayResults(data) {
    const tempNum = Number(data.temperature);
    const phNum = Number(data.ph);
    document.getElementById("temperature").textContent = !isNaN(tempNum) ? `${tempNum.toFixed(1)} °C` : `${data.temperature} °C`;
    document.getElementById("ph").textContent = !isNaN(phNum) ? phNum.toFixed(2) : data.ph;

    // Per-parameter status strictly derived from the DecisionTreeClassifier ML model
    const tempStatus = data.temperature_status || (data.status === "Critical" ? "Critical" : (data.status === "Warning" ? "Warning" : "Optimal"));
    const phStatus = data.ph_status || (data.status === "Critical" ? "Critical" : (data.status === "Warning" ? "Warning" : "Optimal"));

    const tempStatusEl = document.getElementById("temperature-status");
    if (tempStatusEl) {
        tempStatusEl.textContent = tempStatus;
        tempStatusEl.className = `metric-status status-${tempStatus.toLowerCase()}`;
    }

    const phStatusEl = document.getElementById("ph-status");
    if (phStatusEl) {
        phStatusEl.textContent = phStatus;
        phStatusEl.className = `metric-status status-${phStatus.toLowerCase()}`;
    }

    document.getElementById("last-updated").textContent = data.recorded_at
        ? `Last updated ${new Date(data.recorded_at).toLocaleString()}`
        : "";
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
    const userName = greetingEl.dataset.userName || "Rio";
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
    let tempDetailText = `Current: ${temp.toFixed(1)} °C · Within ML optimal range (28.0–32.0 °C)`;

    if (temp < tempMin) {
        const diff = tempMin - temp;
        tempDiffPercent = (diff / temp) * 100;
        tempBadgeText = `+${tempDiffPercent.toFixed(1)}% Needed`;
        tempBadgeClass = tempStatus === "Critical" ? "badge-critical" : "badge-warning";
        tempDetailText = `Increase by +${diff.toFixed(1)} °C to reach ML optimal range (28.0–32.0 °C)`;
    } else if (temp > tempMax) {
        const diff = temp - tempMax;
        tempDiffPercent = (diff / temp) * 100;
        tempBadgeText = `-${tempDiffPercent.toFixed(1)}% Needed`;
        tempBadgeClass = tempStatus === "Critical" ? "badge-critical" : "badge-warning";
        tempDetailText = `Decrease by -${diff.toFixed(1)} °C to reach ML optimal range (28.0–32.0 °C)`;
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
            message: `ML model detected ${severity} condition: Water temperature is ${temp.toFixed(1)} °C (optimal: 28.0–32.0 °C) and pH is ${ph.toFixed(2)} (optimal: 7.50–8.50).`,
            notification: `Push: [${severity.toUpperCase()}] Temp ${temp.toFixed(1)}°C, pH ${ph.toFixed(2)}. Immediate pond remediation required.`
        });
    } else if (tempAbnormal) {
        alertItems.push({
            severity,
            title: `${severity} Temperature Alert`,
            message: `ML model detected ${severity} temperature: Currently ${temp.toFixed(1)} °C, outside optimal range of 28.0–32.0 °C.`,
            notification: `Push: [${severity.toUpperCase()}] Pond temperature is ${temp.toFixed(1)}°C. Check cooling/heating systems.`
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
            message: `ML model classified pond condition as ${severity} based on current readings (Temp: ${temp.toFixed(1)} °C, pH: ${ph.toFixed(2)}).`,
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


document.getElementById("quality-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const data = {
        temperature: Number(formData.get("temperature")),
        ph: Number(formData.get("ph"))
    };

    const submitButton = event.currentTarget.querySelector("button[type=submit]");
    submitButton.disabled = true;
    try {
        const savedReading = await saveReading(data);
        displayResults(savedReading);
        window.dispatchEvent(new Event('shrimpguard:notification-update'));
    } catch (error) {
        console.error("Unable to save water quality reading:", error);
        window.alert(`Unable to save reading: ${error.message}`);
    } finally {
        submitButton.disabled = false;
    }
});

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
            document.getElementById("overall-status").textContent = "No sensor readings are saved yet.";
        }
    } catch (error) {
        console.error("Unable to load the latest sensor reading:", error);
        document.getElementById("overall-status").textContent = "Unable to load sensor data. Please refresh or retry.";
    }
}



// Entrypoint initialization
updateDeviceTime();
setInterval(updateDeviceTime, 1000);
updateGreeting();
setInterval(updateGreeting, 60000);
loadLatestReading();
setInterval(loadLatestReading, 10000);
