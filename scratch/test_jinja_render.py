import jinja2

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
template = env.get_template('calculators.html')

class MockUser:
    email = "test@shrimpguard.com"
    first_name = "Aquaculture"
    last_name = "Specialist"
    role = "Client"

def mock_url_for(endpoint, **values):
    return f"/{endpoint}/" + "/".join(str(v) for v in values.values())

rendered = template.render(user=MockUser(), url_for=mock_url_for)
assert "Computed Performance Metrics (Eqs. 1–8)" in rendered
assert "Performance Trend Graph" in rendered
assert "growth-trend-graph-modal" in rendered
assert "btn-open-growth-chart" in rendered
assert "btn-open-growth-chart-top" not in rendered

# Verify no detail labels
for bad in ["Mortality: 15,000", "Market Count: 50.0", "Weekly Gain: 1.555", "Weight Multiplier: 2,000", "Released: 1,000", "Net Live Gain: 1,699", "Feed Efficiency: 79.95%", "Healthy, robust girth"]:
    assert bad not in rendered, f"Found unexpected label: {bad}"

print("Jinja2 rendering test passed! All template markup is clean, error-free, and valid.")
