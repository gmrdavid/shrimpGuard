with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

def normalize(s):
    return s.replace("\r\n", "\n")

html_norm = normalize(html)

target = """        <div class="modal-dialog-body ai-modal-body">
            <!-- Context Summary Pill Bar -->"""

replacement = """        <div class="modal-dialog-body ai-modal-body">
            <!-- Scope Filter Tabs inside Modal -->
            <div class="ai-modal-tabs" id="ai-modal-tabs" role="tablist" aria-label="AI Decision Support Focus">
                <button type="button" class="ai-modal-tab active" data-tab="all" role="tab" aria-selected="true">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-sparkles"></use></svg>
                    <span>Master Synthesis (All)</span>
                </button>
                <button type="button" class="ai-modal-tab" data-tab="feeding" role="tab" aria-selected="false">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-shrimp"></use></svg>
                    <span>Feeding</span>
                </button>
                <button type="button" class="ai-modal-tab" data-tab="growth" role="tab" aria-selected="false">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                    <span>Growth</span>
                </button>
                <button type="button" class="ai-modal-tab" data-tab="remediation" role="tab" aria-selected="false">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                    <span>Remediation</span>
                </button>
                <button type="button" class="ai-modal-tab" data-tab="ammonia" role="tab" aria-selected="false">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                    <span>Ammonia</span>
                </button>
                <button type="button" class="ai-modal-tab" data-tab="co2" role="tab" aria-selected="false">
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-activity"></use></svg>
                    <span>CO₂</span>
                </button>
            </div>

            <!-- Context Summary Pill Bar -->"""

assert normalize(target) in html_norm, "target not found"
html_norm = html_norm.replace(normalize(target), normalize(replacement), 1)

with open("templates/calculators.html", "w", encoding="utf-8") as f:
    f.write(html_norm)

print("Added AI modal tabs to templates/calculators.html successfully!")

