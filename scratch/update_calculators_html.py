import re

with open("templates/calculators.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove duplicate button #btn-open-growth-chart-top
btn_pattern = re.compile(
    r'\s*<button type="button" id="btn-open-growth-chart-top".*?<\/button>',
    re.DOTALL
)
content, count_btn = btn_pattern.subn('', content, count=1)
print(f"Removed btn-open-growth-chart-top: {count_btn}")

# 2. Remove each of the 8 res-card-detail elements
details = [
    '<p class="res-card-detail">Mortality: <strong id="gm-res-mortality-count">15,000</strong> (<span id="gm-res-mortality-pct">15.00%</span>)</p>',
    '<p class="res-card-detail">Market Count: <strong id="gm-res-count-per-kg">50.0</strong> pcs / kg</p>',
    '<p class="res-card-detail">Weekly Gain: <strong id="gm-res-weekly-gain">1.555</strong> g / week</p>',
    '<p class="res-card-detail">Weight Multiplier: <strong id="gm-res-weight-mult">2,000&times;</strong></p>',
    '<p class="res-card-detail">Released: <strong id="gm-res-ib-grams">1,000</strong> g biological mass</p>',
    '<p class="res-card-detail">Net Live Gain: <strong id="gm-res-net-biomass">1,699.00</strong> kg</p>',
    '<p class="res-card-detail">Feed Efficiency: <strong id="gm-res-feed-efficiency">79.95%</strong> (Feed: <span id="gm-res-tfg-summary">2,125.0 kg</span>)</p>',
    '<p class="res-card-detail">Profile: <strong id="gm-res-k-profile">Healthy, robust girth</strong></p>',
]

for d in details:
    if d in content:
        content = content.replace(d, '')
        print(f"Removed: {d[:30]}...")
    else:
        print(f"WARNING: not found: {d[:30]}...")

with open("templates/calculators.html", "w", encoding="utf-8", newline="\r\n") as f:
    f.write(content)

print("Updated templates/calculators.html successfully.")
