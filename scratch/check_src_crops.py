from PIL import Image

src = Image.open('C:/Users/gliam/.gemini/antigravity/brain/e8e228c4-35c3-4984-b02d-637653b89188/.user_uploaded/media_1794117053190_da0c1993.jpg')
w, h = src.size
print(f"Source image size: {w}x{h}")

# The user uploaded image has:
# Layer 1: y ~ 20 to 140
# Layer 2: y ~ 160 to 380
# Layer 3: y ~ 410 to 520
# Layer 4: y ~ 550 to 660
# Layer 5: y ~ 690 to 780
# Layer 6: y ~ 800 to 900
# Layer 7: y ~ 910 to 970
