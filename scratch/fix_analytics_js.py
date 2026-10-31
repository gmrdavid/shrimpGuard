with open('static/js/analytics.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace ML_RANGES
old_ranges = """const ML_RANGES = {
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
};"""

new_ranges = """const ML_RANGES = {
    temperature: {
        optimalMin: 28.0,
        optimalMax: 32.0,
        warningMin: 25.0,
        warningMax: 33.5,
        unit: "°C"
    },
    ph: {
        optimalMin: 7.50,
        optimalMax: 8.50,
        warningMin: 6.50,
        warningMax: 9.00,
        unit: ""
    }
};"""

if old_ranges in c:
    c = c.replace(old_ranges, new_ranges)
    print("Updated ML_RANGES")

# Replace getAdjustmentStatus hot check
old_hot = 'const text = isTemp ? "Critical: Too hot" : (val > ML_RANGES.ph.warningMax ? "Critical: Too alkaline" : "Warning: Too alkaline");'
new_hot = 'const text = isTemp ? (val > ML_RANGES.temperature.warningMax ? "Critical: Too hot" : "Warning: Too warm") : (val > ML_RANGES.ph.warningMax ? "Critical: Too alkaline" : "Warning: Too alkaline");'

if old_hot in c:
    c = c.replace(old_hot, new_hot)
    print("Updated getAdjustmentStatus hot text")

# Replace getReadingQuality
old_quality = """    // Temperature penalties based on ML boundaries
    if (temp <= ML_RANGES.temperature.warningMin || temp > ML_RANGES.temperature.optimalMax) {
        score -= 25; // Critical
    } else if (temp < ML_RANGES.temperature.optimalMin) {
        score -= 10; // Warning
    }"""

new_quality = """    // Temperature penalties based on ML boundaries
    if (temp <= ML_RANGES.temperature.warningMin || temp > ML_RANGES.temperature.warningMax) {
        score -= 25; // Critical
    } else if (temp < ML_RANGES.temperature.optimalMin || temp > ML_RANGES.temperature.optimalMax) {
        score -= 10; // Warning
    }"""

if old_quality in c:
    c = c.replace(old_quality, new_quality)
    print("Updated getReadingQuality")

# Replace getAlertCounts
old_alert_counts = """        const tempCritical = temp <= ML_RANGES.temperature.warningMin || temp > ML_RANGES.temperature.optimalMax;
        const tempWarning = !tempCritical && temp < ML_RANGES.temperature.optimalMin;"""

new_alert_counts = """        const tempCritical = temp <= ML_RANGES.temperature.warningMin || temp > ML_RANGES.temperature.warningMax;
        const tempWarning = !tempCritical && (temp < ML_RANGES.temperature.optimalMin || temp > ML_RANGES.temperature.optimalMax);"""

if old_alert_counts in c:
    c = c.replace(old_alert_counts, new_alert_counts)
    print("Updated getAlertCounts")

with open('static/js/analytics.js', 'w', encoding='utf-8') as f:
    f.write(c)
print("Finished updating analytics.js")

