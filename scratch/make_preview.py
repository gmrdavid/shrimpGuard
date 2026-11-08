from PIL import Image

img = Image.open('static/images/system_architecture_diagram.png')
print("Image dimensions:", img.size)

# Save a downscaled thumbnail preview for inspection
thumb = img.resize((650, 1100), Image.Resampling.LANCZOS)
thumb.save('scratch/diagram_preview.png')
print("Saved preview to scratch/diagram_preview.png")
