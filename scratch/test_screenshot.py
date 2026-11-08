import os
import subprocess
from pathlib import Path

html_path = Path("scratch/test.html").resolve()
html_path.write_text("<html><body style='background:#126b4f;color:white;font-size:32px;display:flex;align-items:center;justify-content:center;height:100vh;'>ShrimpGuard Test</body></html>", encoding="utf-8")

png_path = Path("scratch/test.png").resolve()
if png_path.exists():
    png_path.unlink()

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
cmd = [
    edge_path,
    "--headless",
    "--disable-gpu",
    "--hide-scrollbars",
    f"--screenshot={png_path}",
    "--window-size=800,400",
    html_path.as_uri()
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)
print("PNG exists:", png_path.exists())
if png_path.exists():
    print("PNG size:", png_path.stat().st_size)
