import re

content = open('templates/admin.html', encoding='utf-8').read()

# 1. VIEW DIALOG
assert 'id="view-user-dialog"' in content
assert 'id="view-user-avatar"' in content
assert 'id="view-user-name"' in content
assert 'id="view-user-email"' in content
assert 'id="view-user-role"' in content
assert 'id="view-user-status"' in content
assert 'id="view-user-last-login"' in content
assert 'id="view-user-export-btn"' in content

# 2. EDIT DIALOG
assert 'id="edit-user-dialog"' in content
assert 'id="edit-user-form"' in content
assert 'id="edit-user-current-email"' in content
assert 'id="edit-user-name"' in content
assert 'id="edit-user-email"' in content
assert 'id="edit-user-role"' in content
assert 'id="edit-user-role-btn"' in content
assert 'id="edit-user-role-menu"' in content
assert 'id="edit-user-status"' in content
assert 'id="edit-user-status-btn"' in content
assert 'id="edit-user-status-menu"' in content
assert 'id="edit-user-new-password"' in content
assert 'id="edit-user-pw-hint"' in content

# 3. ADD DIALOG
assert 'id="add-user-dialog"' in content
assert 'id="new-user-name"' in content
assert 'id="new-user-email"' in content
assert 'id="new-user-role"' in content
assert 'id="new-user-status"' in content
assert 'id="new-user-password"' in content

# 4. Check for removed wordy fluff
assert 'Account information is displayed according to your' not in content
assert 'Most recent recorded account sign-in' not in content
assert 'Update the fields below and save your changes' not in content
assert 'Personal Information\n                            </h3>\n                            <p>Update the user\'s name and email address' not in content

print("All modals, IDs, form inputs, and concise text verified successfully!")
