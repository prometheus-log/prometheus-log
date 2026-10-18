from pillow_heif import register_heif_opener
register_heif_opener()

import sys
import cv2
import numpy as np
from PIL import Image, ImageOps
from rembg import remove, new_session

RAMP = " .`:-=+*cs#%@"   # blank -> dense (13 levels)
COLS = 90                # characters across
CHAR_ASPECT = 0.48       # monospace chars are ~2x taller than wide
CLAHE_CLIP = 3.0
GAMMA = 1.7              # darkening curve

src = sys.argv[1] if len(sys.argv) > 1 else "photo.jpg"

# 1. load, fix phone rotation (HEIC), cap the working size
img = Image.open(src)
img = ImageOps.exif_transpose(img).convert("RGB")
img.thumbnail((1600, 1600))

# 2. cut out the background (u2net = small ~176 MB model)
session = new_session("u2net")
cut = remove(img, session=session).convert("RGBA")
alpha = np.array(cut)[:, :, 3].astype(np.float32) / 255.0
gray = cv2.cvtColor(np.array(cut.convert("RGB")), cv2.COLOR_RGB2GRAY).astype(np.float32)

# force everything outside the subject to white
gray = gray * alpha + 255.0 * (1.0 - alpha)
gray = gray.astype(np.uint8)

# 3. smooth skin, keep edges
gray = cv2.bilateralFilter(gray, 9, 50, 50)

# 4. local contrast
clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP, tileGridSize=(8, 8))
gray = clahe.apply(gray)

# 5. darkening curve
v = (gray.astype(np.float32) / 255.0) ** GAMMA

# 6. downscale to the character grid
h, w = v.shape
rows = int(COLS * (h / w) * CHAR_ASPECT)
v = cv2.resize(v, (COLS, rows), interpolation=cv2.INTER_AREA)
a = cv2.resize(alpha, (COLS, rows), interpolation=cv2.INTER_AREA)
v = np.where(a < 0.5, 1.0, v)   # background stays blank

# 7. map brightness to characters (dark -> dense)
idx = np.clip(np.round((1.0 - v) * (len(RAMP) - 1)).astype(int), 0, len(RAMP) - 1)
lines = ["".join(RAMP[i] for i in row) for row in idx]

with open("portrait.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("\n".join(lines))
print(f"\n{COLS} cols x {rows} rows -> saved portrait.txt")