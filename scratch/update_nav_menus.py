import re

files = [
    'templates/dashboard.html',
    'templates/monitoring.html',
    'templates/historical.html',
    'templates/analytics.html',
    'templates/alerts.html',
    'templates/settings.html'
]

calc_nav_item = """            <a href="/calculators">
                <svg class="ui-icon" aria-hidden="true">
                    <use href="#icon-calculator"></use>
                </svg>
                <span>Aquaculture Tools</span>
            </a>

"""

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # Update logo link
    c = re.sub(r'<a\s+href="/"(\s+class="logo\s+[^"]*"\s+aria-label="ShrimpGuard dashboard">)', r'<a href="/dashboard"\1', c)
    
    # Update Dashboard nav link href="/" to href="/dashboard"
    # But preserve class="active" or other attributes
    c = re.sub(r'<a\s+href="/"(\s+class="active"[^>]*)>', r'<a href="/dashboard"\1>', c)
    c = re.sub(r'<a\s+href="/"(\s*>)', r'<a href="/dashboard"\1>', c)
    
    # Insert Aquaculture Tools before Settings if not already present
    if '/calculators' not in c:
        # Locate Settings link in nav
        settings_pattern = r'(\s*<a\s+href="/settings"[^>]*>.*?<span>Settings</span>.*?</a>)'
        m = re.search(settings_pattern, c, re.DOTALL)
        if m:
            settings_str = m.group(1)
            c = c.replace(settings_str, calc_nav_item + settings_str, 1)
            print(f"Updated nav in {path}")
        else:
            print(f"WARNING: Settings link not found in {path}")
    else:
        print(f"/calculators already present in {path}")
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

print("Done updating navigation menus in existing templates.")

