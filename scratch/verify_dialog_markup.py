import re
from html.parser import HTMLParser

with open('templates/admin.html', encoding='utf-8') as f:
    content = f.read()

# Check dialog structure
dialog_match = re.search(r'<dialog[^>]*id="add-user-dialog"[^>]*>(.*?)</dialog>', content, re.DOTALL)
assert dialog_match, "add-user-dialog not found!"
dialog_html = dialog_match.group(0)

# Verify key elements
assert 'id="new-user-name"' in dialog_html, "new-user-name input missing"
assert 'id="new-user-email"' in dialog_html, "new-user-email input missing"
assert 'id="new-user-role"' in dialog_html, "new-user-role select missing"
assert 'id="new-user-role-btn"' in dialog_html, "new-user-role-btn missing"
assert 'id="new-user-role-menu"' in dialog_html, "new-user-role-menu missing"
assert 'id="new-user-status"' in dialog_html, "new-user-status select missing"
assert 'id="new-user-status-btn"' in dialog_html, "new-user-status-btn missing"
assert 'id="new-user-status-menu"' in dialog_html, "new-user-status-menu missing"
assert 'id="new-user-password"' in dialog_html, "new-user-password input missing"
assert 'admin-pw-toggle-btn' in dialog_html, "password toggle missing"
assert 'new-user-pw-hint' in dialog_html, "password hint missing"
assert 'admin-user-submit' in dialog_html, "submit button missing"
assert 'admin-user-cancel' in dialog_html, "cancel button missing"

print("All elements verified in add-user-dialog!")
