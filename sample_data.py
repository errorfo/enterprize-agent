import os
from PIL import Image, ImageDraw, ImageFont
import csv

OUT_DIR = 'sample_data'
os.makedirs(OUT_DIR, exist_ok=True)
NUM_IMAGES = 6

for i in range(NUM_IMAGES):
    img = Image.new('RGB', (640, 480), color=(200, 220, 255))
    d = ImageDraw.Draw(img)
    text = f"SKU123 - img{i+1}"
    d.text((30, 30), text, fill=(0, 0, 0))
    fname = os.path.join(OUT_DIR, f"img_{i+1}.jpg")
    img.save(fname)

# Create simple inventory CSV
with open(os.path.join(OUT_DIR, 'inventory.csv'), 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['sku', 'expected_quantity'])
    writer.writerow(['SKU123', 2])

print(f"Wrote {NUM_IMAGES} images and inventory.csv to {OUT_DIR}")