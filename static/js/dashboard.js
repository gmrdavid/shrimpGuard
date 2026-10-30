function displayResults(data) {
    document.getElementById("temperature").textContent = `${data.temperature} °C`;
    document.getElementById("ph").textContent = data.ph;
    const needsAttention = data.temperature < 26 || data.temperature > 32 ||
        data.ph < 7.5 || data.ph > 8.5;
    document.getElementById("temperature-status").textContent =
        data.temperature < 26 || data.temperature > 32 ? "Outside recommended range" : "Within recommended range";
    document.getElementById("ph-status").textContent =
        data.ph < 7.5 || data.ph > 8.5 ? "Outside recommended range" : "Within recommended range";
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
    const userName = greetingEl.dataset.userName || "Admin";
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
    const temp = Number(data.temperature);
    const ph = Number(data.ph);

    // 1. Calculate Overall Water Quality Index Accuracy Score
    let wqi = 100;
    // Temperature: optimal 28–32; warning 25–28; critical <= 25 or > 32
    if (temp <= 25.0 || temp > 32.0) {
        wqi -= 25; // Critical penalty
    } else if (temp < 28.0) {
        wqi -= 10; // Warning penalty
    }

    // pH: optimal 7.50–8.50; warning 6.50–7.49 or 8.51–9.0; critical <= 6.49 or > 9.0
    if (ph <= 6.49 || ph > 9.0) {
        wqi -= 25; // Critical penalty
    } else if (ph < 7.50 || ph > 8.50) {
        wqi -= 10; // Warning penalty
    }

    const accuracyScore = Math.max(0, wqi);

    // Update Circle Value
    const wqiValueEl = document.getElementById("wqi-value");
    if (wqiValueEl) {
        wqiValueEl.textContent = `${accuracyScore}%`;
    }

    // Determine status label & theme
    let statusLabel = "OPTIMAL QUALITY";
    let statusTheme = "optimal";
    if (accuracyScore < 70) {
        statusLabel = "CRITICAL CONDITION";
        statusTheme = "critical";
    } else if (accuracyScore < 90) {
        statusLabel = "WARNING CONDITION";
        statusTheme = "warning";
    }

    const wqiStatusEl = document.getElementById("wqi-status");
    if (wqiStatusEl) {
        wqiStatusEl.textContent = statusLabel;
        wqiStatusEl.className = `wqi-status-heading status-${statusTheme}`;
    }

    // 2. Mathematical Equation for Temperature Normalization Percentage:
    // Optimal normal range: [28.0 °C, 32.0 °C]
    // Δ% = (|Boundary - Current| / Current) * 100%
    const tempMin = 28.0;
    const tempMax = 32.0;
    let tempDiffPercent = 0.0;
    let tempBadgeText = "Normal";
    let tempBadgeClass = "badge-normal";
    let tempDetailText = `Current: ${temp.toFixed(1)} °C · Within optimal range (28.0–32.0 °C)`;

    if (temp < tempMin) {
        const diff = tempMin - temp;
        tempDiffPercent = (diff / temp) * 100;
        tempBadgeText = `+${tempDiffPercent.toFixed(1)}% Needed`;
        tempBadgeClass = "badge-warning";
        tempDetailText = `Increase by +${diff.toFixed(1)} °C to reach normal 28.0 °C`;
    } else if (temp > tempMax) {
        const diff = temp - tempMax;
        tempDiffPercent = (diff / temp) * 100;
        tempBadgeText = `-${tempDiffPercent.toFixed(1)}% Needed`;
        tempBadgeClass = "badge-warning";
        tempDetailText = `Decrease by -${diff.toFixed(1)} °C to reach normal 32.0 °C`;
    }

    const tempPercentEl = document.getElementById("temp-norm-percent");
    if (tempPercentEl) {
        tempPercentEl.textContent = tempDiffPercent === 0 ? "0.0%" : (temp < tempMin ? `+${tempDiffPercent.toFixed(1)}%` : `-${tempDiffPercent.toFixed(1)}%`);
    }
    const tempBadgeEl = document.getElementById("temp-norm-badge");
    if (tempBadgeEl) {
        tempBadgeEl.textContent = tempBadgeText;
        tempBadgeEl.className = `wqi-metric-badge ${tempBadgeClass}`;
    }
    const tempDetailEl = document.getElementById("temp-norm-detail");
    if (tempDetailEl) {
        tempDetailEl.textContent = tempDetailText;
    }

    // 3. Mathematical Equation for pH Level Normalization Percentage:
    // Optimal normal range: [7.50, 8.50]
    // Δ% = (|Boundary - Current| / Current) * 100%
    const phMin = 7.50;
    const phMax = 8.50;
    let phDiffPercent = 0.0;
    let phBadgeText = "Normal";
    let phBadgeClass = "badge-normal";
    let phDetailText = `Current: ${ph.toFixed(2)} · Within optimal range (7.50–8.50 pH)`;

    if (ph < phMin) {
        const diff = phMin - ph;
        phDiffPercent = (diff / ph) * 100;
        phBadgeText = `+${phDiffPercent.toFixed(1)}% Needed`;
        phBadgeClass = "badge-warning";
        phDetailText = `Increase by +${diff.toFixed(2)} to reach normal 7.50 pH`;
    } else if (ph > phMax) {
        const diff = ph - phMax;
        phDiffPercent = (diff / ph) * 100;
        phBadgeText = `-${phDiffPercent.toFixed(1)}% Needed`;
        phBadgeClass = "badge-warning";
        phDetailText = `Decrease by -${diff.toFixed(2)} to reach normal 8.50 pH`;
    }

    const phPercentEl = document.getElementById("ph-norm-percent");
    if (phPercentEl) {
        phPercentEl.textContent = phDiffPercent === 0 ? "0.0%" : (ph < phMin ? `+${phDiffPercent.toFixed(1)}%` : `-${phDiffPercent.toFixed(1)}%`);
    }
    const phBadgeEl = document.getElementById("ph-norm-badge");
    if (phBadgeEl) {
        phBadgeEl.textContent = phBadgeText;
        phBadgeEl.className = `wqi-metric-badge ${phBadgeClass}`;
    }
    const phDetailEl = document.getElementById("ph-norm-detail");
    if (phDetailEl) {
        phDetailEl.textContent = phDetailText;
    }

    // 4. Update Overall Assessment Accuracy Metric Card
    const accuracyPercentEl = document.getElementById("wqi-accuracy-percent");
    if (accuracyPercentEl) {
        accuracyPercentEl.textContent = `${accuracyScore}%`;
    }
    const accuracyBadgeEl = document.getElementById("wqi-accuracy-badge");
    if (accuracyBadgeEl) {
        accuracyBadgeEl.textContent = statusLabel;
        accuracyBadgeEl.className = `wqi-metric-badge badge-${statusTheme}`;
    }
    const accuracyDetailEl = document.getElementById("wqi-accuracy-detail");
    if (accuracyDetailEl) {
        accuracyDetailEl.textContent = `Water Quality Index assessment accuracy rating`;
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
