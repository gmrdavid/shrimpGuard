from PIL import Image

img = Image.open('static/images/system_architecture_diagram.png')
print("Image dimensions:", img.size)

# Generate a preview at 561 width (matching original user image width)
orig_ratio = 561 / img.width
target_h = int(img.height * orig_ratio)
preview = img.resize((561, target_h), Image.Resampling.LANCZOS)
preview.save('scratch/preview_561w.png')
print(f"Saved preview: 561x{target_h}")
