with open('templates/_icon_sprite.html', 'r', encoding='utf-8') as f:
    content = f.read()

calc_symbol = """    <symbol id="icon-calculator" viewBox="0 0 24 24">
        <rect x="4" y="2" width="16" height="20" rx="2" />
        <line x1="8" y1="6" x2="16" y2="6" />
        <line x1="16" y1="14" x2="16" y2="18" />
        <path d="M16 10h.01M12 10h.01M8 10h.01M12 14h.01M8 14h.01M12 18h.01M8 18h.01" />
    </symbol>
"""

if 'id="icon-calculator"' not in content:
    target = '<symbol id="icon-settings"'
    content = content.replace(target, calc_symbol + '    ' + target, 1)
    with open('templates/_icon_sprite.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added icon-calculator successfully")
else:
    print("icon-calculator already present")

