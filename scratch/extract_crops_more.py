from PIL import Image

src = Image.open('C:/Users/gliam/.gemini/antigravity/brain/e8e228c4-35c3-4984-b02d-637653b89188/.user_uploaded/media_1794117053190_da0c1993.jpg')

# Let's crop the antenna and the UI icons from layer 6:
crops_more = {
    "lora_antenna": (250, 460, 310, 520),
    "ui_realtime": (50, 850, 115, 905),
    "ui_history": (145, 850, 205, 905),
    "ui_ml": (245, 850, 305, 905),
    "ui_alerts": (345, 850, 405, 905),
    "ui_ai": (445, 850, 505, 905),
    "ntfy_phone": (320, 715, 380, 765),
    "system_alert_bell": (440, 715, 500, 765),
}

for name, box in crops_more.items():
    c = src.crop(box)
    c.save(f'scratch/crops/{name}.png')
    print(f"Cropped {name}: {c.size}")
