import glob
import re

for filepath in sorted(glob.glob('templates/admin*.html')):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    select_matches = re.findall(r'<select[^>]*>', content, re.IGNORECASE)
    btn_dropdown_matches = re.findall(r'<button[^>]*class="[^"]*dropdown[^"]*"[^>]*>', content, re.IGNORECASE)
    menu_matches = re.findall(r'<div[^>]*class="[^"]*dropdown[^"]*"[^>]*>', content, re.IGNORECASE)
    anchor_matches = re.findall(r'class="[^"]*picker-anchor[^"]*"', content, re.IGNORECASE)
    
    print(f"=== {filepath} ===")
    print(f"  Select count: {len(select_matches)}")
    for s in select_matches:
        print(f"    {s.strip()}")
    print(f"  Dropdown buttons: {len(btn_dropdown_matches)}")
    for b in btn_dropdown_matches:
        print(f"    {b.strip()}")
    print(f"  Dropdown divs: {len(menu_matches)}")
    for m in menu_matches:
        print(f"    {m.strip()}")
    print()
