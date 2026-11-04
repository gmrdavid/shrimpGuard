with open("app.py", "rb") as f:
    code = f.read().decode("utf-8")

# 1. generate_alerts_from_readings
target1 = 'status_label = "Active" if is_active else "Resolved"'
replacement1 = 'status_label = "Active" if is_active else "Normalized"'

# 2. get_alerts
target2 = 'resolved_count = len(readings) - len(active_alerts)'
replacement2 = 'normalized_count = len(readings) - len(active_alerts)\n    resolved_count = normalized_count'

target3 = 'status_label = "Active" if (idx == 0 and is_abnormal) else "Resolved"'
replacement3 = 'status_label = "Active" if (idx == 0 and is_abnormal) else "Normalized"'

target4 = 'status_label = "Active" if is_active else "Resolved"'

target5 = '"resolved_count": resolved_count,'
replacement5 = '"normalized_count": normalized_count,\n            "resolved_count": resolved_count,'

# Apply replacements
if target1 in code:
    code = code.replace(target1, replacement1, 1)
    print("Replaced target1")

if target2 in code:
    code = code.replace(target2, replacement2, 1)
    print("Replaced target2")

if target3 in code:
    code = code.replace(target3, replacement3, 1)
    print("Replaced target3")

# target4 appears in history_items loop
if target1 in code: # because target4 was same string as target1
    code = code.replace(target1, replacement1, 1)
    print("Replaced target4")

if target5 in code:
    code = code.replace(target5, replacement5, 1)
    print("Replaced target5")

with open("app.py", "wb") as f:
    f.write(code.encode("utf-8"))
print("app.py updated successfully!")

