from PIL import Image, ImageOps
from pathlib import Path

INPUT_DIR = Path("./imgs")
OUTPUT_DIR = Path("./imgs_256")
OUTPUT_DIR.mkdir(exist_ok=True)

TARGET = (256, 256)

for img_path in INPUT_DIR.glob("*"):
    if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
        continue

    with Image.open(img_path) as img:
        img = img.convert("RGB")
        # Recorta al centro y luego redimensiona (sin deformar)
        img = ImageOps.fit(img, TARGET, method=Image.LANCZOS, centering=(0.5, 0.5))
        out_path = OUTPUT_DIR / (img_path.stem + ".png")
        img.save(out_path, "PNG")

print("Listo.")