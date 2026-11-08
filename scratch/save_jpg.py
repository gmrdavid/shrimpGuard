from PIL import Image
from pathlib import Path

png_path = Path("static/images/system_architecture_diagram.png")
jpg_path = Path("static/images/system_architecture_diagram.jpg")
artifact_jpg = Path(r"C:\Users\gliam\.gemini\antigravity\brain\e8e228c4-35c3-4984-b02d-637653b89188\system_architecture_diagram.jpg")

img = Image.open(png_path).convert("RGB")
img.save(jpg_path, format="JPEG", quality=95)
img.save(artifact_jpg, format="JPEG", quality=95)

print(f"Saved JPG: {jpg_path} ({jpg_path.stat().st_size} bytes)")
print(f"Saved Artifact JPG: {artifact_jpg} ({artifact_jpg.stat().st_size} bytes)")
