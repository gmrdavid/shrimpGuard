with open("static/css/style.css", "r", encoding="utf-8") as f:
    css = f.read()

def normalize(text):
    return text.replace("\r\n", "\n")

css_norm = normalize(css)

target_icon = """.ammonia-heading-icon {
    background: #e0f4ee;
    color: #0c6a58;
    border: 1px solid #bceae0;
}"""

replacement_icon = """.ammonia-heading-icon {
    background: #e0f4ee;
    color: #0c6a58;
    border: 1px solid #bceae0;
}

.co2-heading-icon {
    background: #e1f5fe;
    color: #0277bd;
    border: 1px solid #b3e5fc;
}"""

assert normalize(target_icon) in css_norm, "target_icon not found"
css_norm = css_norm.replace(normalize(target_icon), normalize(replacement_icon), 1)

with open("static/css/style.css", "w", encoding="utf-8") as f:
    f.write(css_norm)

print("Successfully updated style.css!")

