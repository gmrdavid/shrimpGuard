from PIL import Image
import os

src = Image.open('C:/Users/gliam/.gemini/antigravity/brain/e8e228c4-35c3-4984-b02d-637653b89188/.user_uploaded/media_1794117053190_da0c1993.jpg')
os.makedirs('scratch/crops', exist_ok=True)

crops = {
    "ph_sensor": (60, 20, 140, 125),
    "temp_sensor": (160, 45, 250, 125),
    "esp32": (230, 215, 320, 365),
    "lcd": (55, 230, 150, 285),
    "leds": (370, 220, 410, 275),
    "buzzer": (365, 285, 415, 330),
    "lora_module": (45, 465, 130, 520),
    "lora_gateway": (420, 435, 525, 515),
    "cloud_db": (60, 580, 130, 645),
    "ml_brain": (235, 585, 310, 645),
    "ai_head": (420, 585, 490, 645),
}

for name, box in crops.items():
    cropped = src.crop(box)
    cropped.save(f'scratch/crops/{name}.png')
    print(f"Cropped {name}: {cropped.size}")
