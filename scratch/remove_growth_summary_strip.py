import re

with open("templates/calculators.html", "r", encoding="utf-8") as f:
    html = f.read()

pattern = re.compile(
    r'\s*<!-- Mini Summary Metric Cards Strip.*?-->\s*<div class="growth-graph-summary-strip".*?<\/div>\s*<\/div>',
    re.DOTALL
)

# We want to remove the summary strip, but keep the closing </div> of modal-dialog-body
# Let's inspect exact target:
target = """            <!-- Mini Summary Metric Cards Strip (Eqs. 1-4, 6-8) -->
            <div class="growth-graph-summary-strip">
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 1: Survival</span>
                    <strong id="mini-stat-sr" class="mini-val">-- %</strong>
                    <span id="mini-badge-sr" class="mini-badge badge-optimal">Optimal</span>
                </div>
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 2: FABW</span>
                    <strong id="mini-stat-fabw" class="mini-val">-- g</strong>
                    <span id="mini-sub-fabw" class="mini-sub">-- count/kg</span>
                </div>
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 3: ADWG</span>
                    <strong id="mini-stat-adwg" class="mini-val">-- g/d</strong>
                    <span id="mini-badge-adwg" class="mini-badge badge-optimal">Fast</span>
                </div>
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 4: SGR</span>
                    <strong id="mini-stat-sgr" class="mini-val">-- %/d</strong>
                    <span id="mini-sub-sgr" class="mini-sub">Specific Rate</span>
                </div>
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 6: Final Biomass</span>
                    <strong id="mini-stat-fb" class="mini-val">-- kg</strong>
                    <span id="mini-sub-fb" class="mini-sub">Yield</span>
                </div>
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 7: FCR</span>
                    <strong id="mini-stat-fcr" class="mini-val">--</strong>
                    <span id="mini-badge-fcr" class="mini-badge badge-optimal">Optimal</span>
                </div>
                <div class="graph-mini-card">
                    <span class="mini-label">Eq. 8: Fulton's K</span>
                    <strong id="mini-stat-k" class="mini-val">--</strong>
                    <span id="mini-badge-k" class="mini-badge badge-optimal">Normal</span>
                </div>
            </div>"""

if target in html:
    html = html.replace(target, "")
    print("SUCCESS: Target matched and removed.")
else:
    # Try normalized newlines
    norm_html = html.replace("\r\n", "\n")
    norm_target = target.replace("\r\n", "\n")
    if norm_target in norm_html:
        html = norm_html.replace(norm_target, "")
        print("SUCCESS: Normalized target matched and removed.")
    else:
        print("ERROR: Target not found!")

with open("templates/calculators.html", "w", encoding="utf-8", newline="\r\n") as f:
    f.write(html)

print("Updated templates/calculators.html")

