with open("static/css/style.css", "r", encoding="utf-8") as f:
    css = f.read()

def normalize(s):
    return s.replace("\r\n", "\n")

css_norm = normalize(css)

old_css = """.module-nav-eyebrow {
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #16a34a;
}

.module-nav-title {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
    margin: 2px 0 0;
}

.module-nav-controls {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}

.module-dropdown-wrap {
    position: relative;
    display: inline-block;
}

.tools-btn-choose {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
    color: #ffffff;
    border: 1px solid #16a34a;
    border-radius: 10px;
    padding: 9px 16px;
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(22, 163, 74, 0.28);
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.tools-btn-choose:hover {
    background: linear-gradient(135deg, #15803d 0%, #166534 100%);
    box-shadow: 0 4px 14px rgba(22, 163, 74, 0.38);
    transform: translateY(-1px);
}"""

new_css = """.module-nav-eyebrow {
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #15803d;
}

.module-nav-title {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
    margin: 2px 0 0;
}

.module-nav-controls {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}

.module-dropdown-wrap {
    position: relative;
    display: inline-block;
}

.tools-btn-choose {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, #15803d 0%, #166534 100%);
    color: #ffffff;
    border: 1px solid #166534;
    border-radius: 10px;
    padding: 9px 16px;
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(21, 128, 61, 0.35);
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.tools-btn-choose:hover {
    background: linear-gradient(135deg, #166534 0%, #14532d 100%);
    box-shadow: 0 4px 14px rgba(22, 101, 52, 0.45);
    transform: translateY(-1px);
}"""

assert normalize(old_css) in css_norm, "old_css target not found"
css_norm = css_norm.replace(normalize(old_css), normalize(new_css), 1)

with open("static/css/style.css", "w", encoding="utf-8") as f:
    f.write(css_norm)

print("Darker green applied to static/css/style.css successfully!")

