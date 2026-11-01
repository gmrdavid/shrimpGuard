with open("templates/historical.html", "r", encoding="utf-8") as f:
    html = f.read()

def normalize(text):
    return text.replace("\r\n", "\n")

html_norm = normalize(html)

# 1. Remove interval filter from historical-filter-form
old_interval = """                <label for="history-interval" class="historical-filter-label">
                    <span>Time Interval</span>
                    <select id="history-interval">
                        <option value="all">All available</option>
                        <option value="1">Last hour</option>
                        <option value="6">Last 6 hours</option>
                        <option value="12">Last 12 hours</option>
                        <option value="24">Last 24 hours</option>
                        <option value="168">Last 7 days</option>
                    </select>
                </label>"""

assert normalize(old_interval) in html_norm, "old_interval not found"
html_norm = html_norm.replace(normalize(old_interval) + "\n\n", "")
if normalize(old_interval) in html_norm:
    html_norm = html_norm.replace(normalize(old_interval), "")

# 2. Remove export button in water quality trend
old_chart_export = """                    <div class="history-export-actions historical-export-actions">

                        <span id="history-count" class="historical-count-badge">
                            0 readings
                        </span>

                        <button id="history-export-button" class="historical-toolbar-btn historical-download-btn" type="button" aria-label="Export readings" title="Export readings by date & status">
                            <svg class="ui-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M12 3v12"></path>
                                <path d="m7 10 5 5 5-5"></path>
                                <path d="M5 17v4h14v-4"></path>
                            </svg>
                            <span>Export</span>
                        </button>

                    </div>"""

new_chart_export = """                    <div class="history-export-actions historical-export-actions">

                        <span id="history-count" class="historical-count-badge">
                            0 readings
                        </span>

                    </div>"""

assert normalize(old_chart_export) in html_norm, "old_chart_export not found"
html_norm = html_norm.replace(normalize(old_chart_export), normalize(new_chart_export), 1)

with open("templates/historical.html", "w", encoding="utf-8") as f:
    f.write(html_norm)

print("Updated templates/historical.html successfully!")

# Now update static/js/historical.js
with open("static/js/historical.js", "r", encoding="utf-8") as f:
    js = f.read()

js_norm = normalize(js)

old_filter_fn = """function filterHistory(history) {
    const selectedDate = document.getElementById("history-date").value;
    const interval = document.getElementById("history-interval").value;
    const now = Date.now();
    return history.filter((reading) => {
        const recorded = new Date(reading.recorded_at).getTime();
        const dateMatches = !selectedDate || localDate(reading) === selectedDate;
        const intervalMatches = interval === "all" || now - recorded <= Number(interval) * 60 * 60 * 1000;
        return dateMatches && intervalMatches;
    });
}"""

new_filter_fn = """function filterHistory(history) {
    const selectedDate = document.getElementById("history-date")?.value;
    const intervalEl = document.getElementById("history-interval");
    const interval = intervalEl ? intervalEl.value : "all";
    const now = Date.now();
    return history.filter((reading) => {
        const recorded = new Date(reading.recorded_at).getTime();
        const dateMatches = !selectedDate || localDate(reading) === selectedDate;
        const intervalMatches = interval === "all" || now - recorded <= Number(interval) * 60 * 60 * 1000;
        return dateMatches && intervalMatches;
    });
}"""

assert normalize(old_filter_fn) in js_norm, "old_filter_fn not found"
js_norm = js_norm.replace(normalize(old_filter_fn), normalize(new_filter_fn), 1)

with open("static/js/historical.js", "w", encoding="utf-8") as f:
    f.write(js_norm)

print("Updated static/js/historical.js successfully!")

