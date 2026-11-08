import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

# Let's inspect 4 crops of the diagram to verify quality:
img = Image.open('static/images/system_architecture_diagram.png')
w, h = img.size

# Crop top (Layers 1 & 2), middle (Layers 3 & 4), bottom (Layers 5, 6, 7)
c1 = img.crop((0, 0, w, int(h * 0.35)))
c2 = img.crop((0, int(h * 0.32), w, int(h * 0.68)))
c3 = img.crop((0, int(h * 0.65), w, h))

c1.save('scratch/crop_layer1_2.png')
c2.save('scratch/crop_layer3_4.png')
c3.save('scratch/crop_layer5_6_7.png')
print("Saved 3 inspection crops.")
