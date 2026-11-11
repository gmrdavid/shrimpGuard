import subprocess
import json
import os
import time

server_path = r"C:\Users\gliam\AppData\Local\Programs\Microsoft VS Code\c4453f8ea4\resources\app\extensions\css-language-features\server\dist\node\cssServerMain.js"
css_file = os.path.abspath("static/css/style.css")

with open(css_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

total_lines = len(lines)
chunk_size = 1000

print(f"Total lines: {total_lines}, testing in chunks of {chunk_size}...")

# Let's test the entire file or chunks
# Wait, let's see why the entire file returned 0 diagnostics in LSP.
# Does VS Code have a maxProblems limit, or did it return 0 because there really are 0 syntax errors according to CSS parser?
