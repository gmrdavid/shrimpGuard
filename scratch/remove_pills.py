with open("templates/calculators.html", "r", encoding="utf-8") as f:
    text = f.read()

def normalize(s):
    return s.replace("\r\n", "\n")

text_norm = normalize(text)

pills_block = """                    <!-- Quick Segmented Pill Tabs for 1-click switching -->
                    <div class="module-nav-pills" id="tools-module-pills" role="tablist" aria-label="Calculation Modules">
                        <button type="button" class="module-pill active" data-module="feeding" role="tab" aria-selected="true">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-shrimp"></use></svg>
                            <span>Feeding Management</span>
                        </button>
                        <button type="button" class="module-pill" data-module="growth" role="tab" aria-selected="false">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-chart"></use></svg>
                            <span>Growth Performance</span>
                        </button>
                        <button type="button" class="module-pill" data-module="remediation" role="tab" aria-selected="false">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                            <span>Water Remediation</span>
                        </button>
                        <button type="button" class="module-pill" data-module="ammonia" role="tab" aria-selected="false">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-droplet"></use></svg>
                            <span>Unionized Ammonia</span>
                        </button>
                        <button type="button" class="module-pill" data-module="co2" role="tab" aria-selected="false">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-activity"></use></svg>
                            <span>Carbon Dioxide</span>
                        </button>
                        <button type="button" class="module-pill pill-all" data-module="all" role="tab" aria-selected="false">
                            <svg class="ui-icon" aria-hidden="true"><use href="#icon-calculator"></use></svg>
                            <span>Show All</span>
                        </button>
                    </div>"""

assert normalize(pills_block) in text_norm, "pills_block not found in calculators.html"

text_norm = text_norm.replace(normalize(pills_block), "")

with open("templates/calculators.html", "w", encoding="utf-8") as f:
    f.write(text_norm)

print("Removed exposed pills from templates/calculators.html successfully!")

