import os
import re

HEAD_SCRIPT = """    <link rel="stylesheet"
          href="{{ url_for('static', filename='css/style.css') }}?v=20261107_dark1">
    <script>
        (function() {
            var t = localStorage.getItem('shrimp_theme');
            var isD = t === 'dark' || (!t && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
            var mode = isD ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', mode);
            document.documentElement.classList.add('theme-' + mode);
        })();
        function toggleShrimpTheme() {
            if (window.ShrimpTheme && window.ShrimpTheme.toggleTheme) {
                return window.ShrimpTheme.toggleTheme();
            }
            var cur = document.documentElement.getAttribute('data-theme') || (document.documentElement.classList.contains('theme-dark') ? 'dark' : 'light');
            var next = cur === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            document.documentElement.classList.remove('theme-dark', 'theme-light');
            document.documentElement.classList.add('theme-' + next);
            if (document.body) {
                document.body.setAttribute('data-theme', next);
                document.body.classList.remove('theme-dark', 'theme-light');
                document.body.classList.add('theme-' + next);
            }
            try { localStorage.setItem('shrimp_theme', next); } catch(e) {}
            var m = document.querySelector('meta[name="theme-color"]');
            if (m) m.setAttribute('content', next === 'dark' ? '#0c151b' : '#126b4f');
            var s = document.getElementById('theme-preference-select');
            if (s) s.value = next;
            window.dispatchEvent(new CustomEvent('shrimp-theme-change', { detail: { theme: next } }));
        }
    </script>"""

BUTTON_HTML = """                <button
                    id="theme-toggle-btn"
                    class="theme-toggle-btn"
                    type="button"
                    onclick="toggleShrimpTheme()"
                    aria-label="Toggle dark mode"
                    title="Toggle dark mode">
                    <svg class="ui-icon theme-icon-moon" aria-hidden="true"><use href="#icon-moon"></use></svg>
                    <svg class="ui-icon theme-icon-sun" aria-hidden="true"><use href="#icon-sun"></use></svg>
                </button>"""

BUTTON_HTML_INDENTED = """            <button
                id="theme-toggle-btn"
                class="theme-toggle-btn"
                type="button"
                onclick="toggleShrimpTheme()"
                aria-label="Toggle dark mode"
                title="Toggle dark mode">
                <svg class="ui-icon theme-icon-moon" aria-hidden="true"><use href="#icon-moon"></use></svg>
                <svg class="ui-icon theme-icon-sun" aria-hidden="true"><use href="#icon-sun"></use></svg>
            </button>"""

THEME_SCRIPT = """<script src="{{ url_for('static', filename='js/theme.js') }}?v=20261107_dark1"></script>"""

templates = [
    "dashboard.html",
    "monitoring.html",
    "devices.html",
    "historical.html",
    "analytics.html",
    "alerts.html",
    "calculators.html",
    "settings.html",
    "admin_dashboard.html",
    "admin.html",
    "admin_telemetry.html",
    "admin_logs.html",
    "login.html",
    "signup.html",
    "landing.html"
]

for tpl in templates:
    path = os.path.join("templates", tpl)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Replace style.css and existing pre-render script in <head>
    # Pattern to match link to style.css and script up to </head>
    pattern_head = r'<link rel="stylesheet"[^>]*href="[^"]*css/style\.css[^"]*"[^>]*>[\s\S]*?</head>'
    new_head = HEAD_SCRIPT + "\n</head>"
    if re.search(pattern_head, content):
        content = re.sub(pattern_head, new_head, content, count=1)
    else:
        print(f"Warning: pattern_head not matched in {tpl}")

    # 2. Update theme-toggle-btn to ensure onclick="toggleShrimpTheme()" is present
    pattern_btn = r'<button\s+id="theme-toggle-btn"[\s\S]*?</button>'
    if "admin" in tpl and tpl not in ["admin_dashboard.html"]:
        content = re.sub(pattern_btn, BUTTON_HTML_INDENTED, content, count=1)
    else:
        content = re.sub(pattern_btn, BUTTON_HTML, content, count=1)

    # 3. Update theme.js script with cache buster
    pattern_script = r'<script\s+src="[^"]*js/theme\.js[^"]*">\s*</script>'
    content = re.sub(pattern_script, THEME_SCRIPT, content, count=1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Updated {tpl}")

print("All templates updated cleanly!")
