with open("templates/alerts.html", "r", encoding="utf-8") as f:
    html = f.read()

def normalize(text):
    return text.replace("\r\n", "\n")

html_norm = normalize(html)

old_unread = """                        <div class="metric-reading" style="display: flex; align-items: baseline; justify-content: space-between;">
                            <h2 id="unread-notifications-count">0</h2>
                            <button id="mark-all-read-btn" type="button" style="background: none; border: none; font-size: 11px; font-weight: 600; color: #16a34a; cursor: pointer; text-decoration: underline; padding: 0;">
                                Mark all as read
                            </button>
                        </div>"""

new_unread = """                        <div class="metric-reading">
                            <h2 id="unread-notifications-count">0</h2>
                        </div>"""

assert normalize(old_unread) in html_norm, "old_unread not found"
html_norm = html_norm.replace(normalize(old_unread), normalize(new_unread), 1)

with open("templates/alerts.html", "w", encoding="utf-8") as f:
    f.write(html_norm)

print("Updated templates/alerts.html successfully!")

