// ML Model Parameter Classification Ranges
const ML_RANGES = {
    temperature: {
        optimalMin: 28.0,
        optimalMax: 32.0,
        warningMin: 25.0,
        unit: "°C"
    },
    ph: {
        optimalMin: 7.50,
        optimalMax: 8.50,
        warningMin: 6.50,
        warningMax: 9.00,
        unit: ""
    }
};

function getAdjustmentStatus(key, value, min, max) {
    const val = Number(value);
    const isTemp = key === "temperature" || key === "temp";
    const unit = isTemp ? "°C" : "";

    if (val < min) {
        const diff = min - val;
        const text = isTemp
            ? (val <= ML_RANGES.temperature.warningMin ? "Critical: Too cold" : "Warning: Too cool")
            : (val <= 6.49 ? "Critical: Too acidic" : "Warning: Too acidic");
        return {
            text: text,
            amount: diff,
            unit: unit,
            sign: "+",
            action: `Increase by +${diff.toFixed(isTemp ? 1 : 2)}${unit} to reach ML optimal ${min.toFixed(isTemp ? 1 : 2)}${unit}`
        };
    }

    if (val > max) {
        const diff = val - max;
        const text = isTemp ? "Critical: Too hot" : (val > ML_RANGES.ph.warningMax ? "Critical: Too alkaline" : "Warning: Too alkaline");
        return {
            text: text,
            amount: diff,
            unit: unit,
            sign: "-",
            action: `Decrease by -${diff.toFixed(isTemp ? 1 : 2)}${unit} to reach ML optimal ${max.toFixed(isTemp ? 1 : 2)}${unit}`
        };
    }

    return {
        text: "ML Optimal",
        amount: 0,
        unit: unit,
        sign: "",
        action: "Within ML optimal range"
    };
}

function getReadingQuality(reading) {
    let score = 100;
    const temp = Number(reading.temperature);
    const ph = Number(reading.ph);

    // Temperature penalties based on ML boundaries
    if (temp <= ML_RANGES.temperature.warningMin || temp > ML_RANGES.temperature.optimalMax) {
        score -= 25; // Critical
    } else if (temp < ML_RANGES.temperature.optimalMin) {
        score -= 10; // Warning
    }

    // pH penalties based on ML boundaries
    if (ph <= 6.49 || ph > ML_RANGES.ph.warningMax) {
        score -= 25; // Critical
    } else if (ph < ML_RANGES.ph.optimalMin || ph > ML_RANGES.ph.optimalMax) {
        score -= 10; // Warning
    }

    return Math.max(0, score);
}

function getAlertCounts(history) {
    return history.reduce((counts, reading) => {
        const temp = Number(reading.temperature);
        const ph = Number(reading.ph);

        const tempCritical = temp <= ML_RANGES.temperature.warningMin || temp > ML_RANGES.temperature.optimalMax;
        const tempWarning = !tempCritical && temp < ML_RANGES.temperature.optimalMin;

        const phCritical = ph <= 6.49 || ph > ML_RANGES.ph.warningMax;
        const phWarning = !phCritical && (ph < ML_RANGES.ph.optimalMin || ph > ML_RANGES.ph.optimalMax);

        if (tempCritical || phCritical) {
            counts.critical += 1;
        } else if (tempWarning || phWarning) {
            counts.warnings += 1;
        }
        return counts;
    }, { critical: 0, warnings: 0 });
}

function setAdjustment(key, value, min, max) {
    const isTemp = key === "temperature" || key === "temp";
    const prefix = isTemp ? "temp" : key;
    const valueElement = document.getElementById(`${prefix}-adjustment`) || document.getElementById(`${key}-adjustment`);
    const statusElement = document.getElementById(`${prefix}-status`) || document.getElementById(`${key}-status`);
    if (!valueElement || !statusElement) return;

    const val = Number(value);
    const adjustment = getAdjustmentStatus(key, val, min, max);

    if (adjustment.amount === 0) {
        valueElement.textContent = isTemp ? "0.0°C" : "0.00";
    } else {
        const formattedAmount = adjustment.amount.toFixed(isTemp ? 1 : 2);
        valueElement.textContent = `${adjustment.sign}${formattedAmount}${adjustment.unit}`;
    }

    const currentStr = `${val.toFixed(isTemp ? 1 : 2)}${adjustment.unit}`;
    if (adjustment.amount === 0) {
        statusElement.textContent = `Current: ${currentStr} (ML Optimal)`;
    } else {
        statusElement.textContent = `Current: ${currentStr} (${adjustment.text} · ${adjustment.sign}${adjustment.amount.toFixed(isTemp ? 1 : 2)}${adjustment.unit} needed)`;
    }
}

function updateOptimalRangeLabels() {
    const tempRangeEl = document.getElementById("temp-optimal-range");
    if (tempRangeEl) {
        tempRangeEl.textContent = `ML Optimal Range: ${ML_RANGES.temperature.optimalMin.toFixed(1)}°C – ${ML_RANGES.temperature.optimalMax.toFixed(1)}°C`;
    }
    const phRangeEl = document.getElementById("ph-optimal-range");
    if (phRangeEl) {
        phRangeEl.textContent = `ML Optimal Range: ${ML_RANGES.ph.optimalMin.toFixed(2)} – ${ML_RANGES.ph.optimalMax.toFixed(2)} pH`;
    }
}

function showNoReadings() {
    updateOptimalRangeLabels();
    document.getElementById("analytics-demo-note").hidden = true;
    document.getElementById("analytics-average-quality").textContent = "--";
    document.getElementById("analytics-quality-summary").textContent = "No sensor readings are saved";
    document.getElementById("analytics-active-alerts").textContent = "0";
    document.getElementById("analytics-alert-summary").textContent = "No readings to evaluate";
    document.getElementById("analytics-recommended-action").textContent = "No data";
    document.getElementById("analytics-action-summary").textContent = "Submit a reading to get an action";
    document.getElementById("analytics-monitoring-status").textContent = "Waiting";
    document.getElementById("analytics-last-update").textContent = "No readings available";
    document.getElementById("analytics-health-heading").textContent = "No sensor readings are available.";
    document.getElementById("analytics-health-detail").textContent = "Submit a dashboard reading to populate the sensor history.";
    document.getElementById("analytics-key-findings").innerHTML = "<li>No sensor readings are available.</li>";
    document.getElementById("analytics-recommended-operations").innerHTML = "<li>Submit a sensor reading to see recommendations.</li>";
    document.getElementById("analytics-report-quality").textContent = "--";
    document.getElementById("analytics-report-critical").textContent = "0";
    document.getElementById("analytics-report-warnings").textContent = "0";
    document.getElementById("analytics-report-updated").textContent = "--";
    document.getElementById("temp-adjustment").textContent = "--";
    document.getElementById("temp-status").textContent = "Waiting for reading";
    document.getElementById("ph-adjustment").textContent = "--";
    document.getElementById("ph-status").textContent = "Waiting for reading";
}

function showUnavailable() {
    updateOptimalRangeLabels();
    document.getElementById("analytics-demo-note").hidden = true;
    document.getElementById("analytics-average-quality").textContent = "--";
    document.getElementById("analytics-quality-summary").textContent = "Sensor database unavailable";
    document.getElementById("analytics-active-alerts").textContent = "--";
    document.getElementById("analytics-alert-summary").textContent = "Unable to load alerts";
    document.getElementById("analytics-recommended-action").textContent = "Unavailable";
    document.getElementById("analytics-action-summary").textContent = "Could not load sensor readings";
    document.getElementById("analytics-monitoring-status").textContent = "Unavailable";
    document.getElementById("analytics-last-update").textContent = "Could not connect to database";
    document.getElementById("analytics-health-heading").textContent = "Sensor data is unavailable.";
    document.getElementById("analytics-health-detail").textContent = "Check the database connection and refresh this page.";
    document.getElementById("analytics-key-findings").innerHTML = "<li>Unable to load sensor data.</li>";
    document.getElementById("analytics-recommended-operations").innerHTML = "<li>Unable to load sensor data.</li>";
    document.getElementById("analytics-report-quality").textContent = "--";
    document.getElementById("analytics-report-critical").textContent = "--";
    document.getElementById("analytics-report-warnings").textContent = "--";
    document.getElementById("analytics-report-updated").textContent = "--";
    document.getElementById("temp-adjustment").textContent = "--";
    document.getElementById("temp-status").textContent = "Sensor data unavailable";
    document.getElementById("ph-adjustment").textContent = "--";
    document.getElementById("ph-status").textContent = "Sensor data unavailable";
}

function renderAnalytics(reading, history, recommendation) {
    if (!reading || history.length === 0) {
        showNoReadings();
        return;
    }

    updateOptimalRangeLabels();

    const counts = getAlertCounts(history);
    const latestDate = new Date(reading.recorded_at);
    const qualityAverage = Math.round(history.reduce((sum, item) => sum + getReadingQuality(item), 0) / history.length);
    const activeAlerts = counts.critical + counts.warnings;
    const outsideRange = reading.temperature < ML_RANGES.temperature.optimalMin ||
        reading.temperature > ML_RANGES.temperature.optimalMax ||
        reading.ph < ML_RANGES.ph.optimalMin ||
        reading.ph > ML_RANGES.ph.optimalMax;

    document.getElementById("analytics-demo-note").hidden =
        !history.some((item) => item.status === "Demo");

    document.getElementById("analytics-average-quality").textContent = `${qualityAverage} / 100`;
    document.getElementById("analytics-quality-summary").textContent =
        `Average across ${history.length} saved readings`;
    document.getElementById("analytics-active-alerts").textContent = String(activeAlerts);
    document.getElementById("analytics-alert-summary").textContent =
        `${counts.critical} critical, ${counts.warnings} warning conditions in saved readings`;
    document.getElementById("analytics-recommended-action").textContent =
        recommendation ? recommendation.classification : "Unavailable";
    
    // Provide a concise actionable summary for the overview metric card
    const shortAction = recommendation
        ? (recommendation.actionable_solution || recommendation.recommendation)
        : "AI recommendations are temporarily unavailable.";
    document.getElementById("analytics-action-summary").textContent = shortAction;
    
    document.getElementById("analytics-monitoring-status").textContent = "Database";
    document.getElementById("analytics-last-update").textContent = latestDate.toLocaleString();
    document.getElementById("analytics-health-heading").textContent = outsideRange
        ? "Latest pond readings need attention (outside ML optimal range)."
        : "Latest pond readings are within ML optimal range.";
    document.getElementById("analytics-health-detail").textContent =
        `Latest temperature: ${reading.temperature} °C; latest pH: ${reading.ph}. ${history.length} readings loaded from the sensors table.`;
    
    // Key Findings: structured bullet points
    const findingsList = [
        `<li>Latest temperature is <strong>${reading.temperature} °C</strong> (${getAdjustmentStatus("temperature", reading.temperature, ML_RANGES.temperature.optimalMin, ML_RANGES.temperature.optimalMax).text.toLowerCase()}).</li>`,
        `<li>Latest pH is <strong>${reading.ph}</strong> (${getAdjustmentStatus("ph", reading.ph, ML_RANGES.ph.optimalMin, ML_RANGES.ph.optimalMax).text.toLowerCase()}).</li>`,
        `<li>${counts.critical} critical and ${counts.warnings} warning conditions across ${history.length} saved readings.</li>`
    ];
    if (recommendation && recommendation.recommendation) {
        const diagSummary = recommendation.recommendation.length > 200
            ? recommendation.recommendation.slice(0, 197) + "..."
            : recommendation.recommendation;
        findingsList.splice(2, 0, `<li><strong>Biological Diagnosis:</strong> ${diagSummary}</li>`);
    }
    document.getElementById("analytics-key-findings").innerHTML = findingsList.join("");

    // Recommended Operations: actionable bullet points from AI
    let opsList = [];
    if (recommendation && Array.isArray(recommendation.actionable_solutions) && recommendation.actionable_solutions.length > 0) {
        opsList = recommendation.actionable_solutions.slice(0, 3).map(action => `<li>${action}</li>`);
    } else if (recommendation && recommendation.actionable_solution) {
        opsList = [`<li>${recommendation.actionable_solution}</li>`];
    } else {
        opsList = [`<li>AI recommendations are temporarily unavailable.</li>`];
    }
    opsList.push(`<li>Review the ${history.length} saved sensor readings and continue regular monitoring.</li>`);
    document.getElementById("analytics-recommended-operations").innerHTML = opsList.join("");
    document.getElementById("analytics-report-quality").textContent = `${qualityAverage} / 100`;
    document.getElementById("analytics-report-critical").textContent = String(counts.critical);
    document.getElementById("analytics-report-warnings").textContent = String(counts.warnings);
    document.getElementById("analytics-report-updated").textContent = latestDate.toLocaleString();

    setAdjustment("temperature", reading.temperature, ML_RANGES.temperature.optimalMin, ML_RANGES.temperature.optimalMax);
    setAdjustment("ph", reading.ph, ML_RANGES.ph.optimalMin, ML_RANGES.ph.optimalMax);
}

async function loadRecommendation(reading) {
    const response = await fetch("/api/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ temperature: reading.temperature, ph: reading.ph })
    });
    if (!response.ok) {
        throw new Error(`Recommendation API returned ${response.status}.`);
    }

    const recommendation = await response.json();
    if (typeof recommendation.classification !== "string" ||
        typeof recommendation.recommendation !== "string") {
        throw new Error("Recommendation response has an invalid format.");
    }
    return recommendation;
}

async function loadSensorAnalytics() {
    try {
        const [latestResponse, historyResponse] = await Promise.all([
            fetch("/api/readings/latest"),
            fetch("/api/readings/history")
        ]);
        if (!latestResponse.ok || !historyResponse.ok) {
            throw new Error(`Sensor API returned ${latestResponse.status} / ${historyResponse.status}.`);
        }

        const [reading, history] = await Promise.all([latestResponse.json(), historyResponse.json()]);
        if (!Array.isArray(history)) throw new Error("Sensor history response has an invalid format.");
        let recommendation = null;
        if (reading && history.length > 0) {
            try {
                recommendation = await loadRecommendation(reading);
            } catch (error) {
                console.error("Unable to load AI recommendations for analytics:", error);
            }
        }
        renderAnalytics(reading, history, recommendation);
    } catch (error) {
        console.error("Unable to load sensor data for analytics:", error);
        showUnavailable();
    }
}

function updateDeviceTime() {
    document.getElementById("time").textContent =
        new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

updateOptimalRangeLabels();
updateDeviceTime();
setInterval(updateDeviceTime, 1000);
loadSensorAnalytics();
setInterval(loadSensorAnalytics, 10000);
