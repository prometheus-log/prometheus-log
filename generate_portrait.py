
"""
generate_portrait.py  -  cartoon/photo -> portrait.txt (ASCII)
Usage:  python generate_portrait.py cartoon_illustration.jpg
Needs only: pillow, pillow-heif (for .heic), numpy, opencv-python-headless. No rembg / no big model.
"""
import sys
import cv2
import numpy as np
from PIL import Image, ImageOps
 
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass
 
RAMP = " .`:-=+*cs#%@"      # blank -> dense
COLS = 150                  # characters across
CHAR_ASPECT = 0.48
GAMMA = 1.4                 # >1 keeps skin light so lines stand out
TONE_WEIGHT = 0.55          # how much soft shading shows
EDGE_GAIN = 12.0
FLOOR = 0.22                # higher = cleaner skin, fewer stray dots            # linework strength
 
src = sys.argv[1] if len(sys.argv) > 1 else "cartoon_illustration.jpg"
img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
img.thumbnail((1400, 1400))
bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
H, W = bgr.shape[:2]
 
# ---- 1. background mask: grab the dominant colour at the image corners/edges
border = np.concatenate([bgr[:12].reshape(-1, 3), bgr[:, :12].reshape(-1, 3), bgr[:, -12:].reshape(-1, 3)])
bg_col = np.median(border, axis=0)
lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
bg_lab = cv2.cvtColor(np.uint8([[bg_col]]), cv2.COLOR_BGR2LAB).astype(np.float32)[0, 0]
dist = np.linalg.norm(lab - bg_lab, axis=2)
fg = (dist > 28).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
 
# ---- 2. find the face, crop: hair top -> a little below the chin
gray0 = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
fc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
faces = fc.detectMultiScale(gray0, 1.1, 4, minSize=(W // 6, W // 6))
if len(faces) == 0:
    sys.exit("Face detect nahi hua - photo/cartoon me chehra seedha aur bada rakho.")
x, y, w, h = max(faces, key=lambda r: r[2])
cut_y = min(H, y + int(h * 1.12))                  # just under the chin
fg[cut_y:, :] = 0                                  # drops shirt + hand
rows_any = np.where(fg.any(axis=1))[0]
cols_any = np.where(fg.any(axis=0))[0]
y0, y1 = rows_any.min(), cut_y
x0, x1 = cols_any.min(), cols_any.max()
pad = 8
y0, x0 = max(0, y0 - pad), max(0, x0 - pad)
x1, y1 = min(W, x1 + pad), min(H, y1 + pad)
 
bgr, fg = bgr[y0:y1, x0:x1], fg[y0:y1, x0:x1]
alpha = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 1.5)
 
# ---- 3. tones = light fills + strong linework (this is what makes it read as a face)
bgr = cv2.bilateralFilter(bgr, 9, 40, 9)            # kill paper/skin texture, keep outlines
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
lo, hi = np.percentile(gray[alpha > 0.5], [1, 99])
g = np.clip((gray - lo) / (hi - lo), 0, 1)
g = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply((g * 255).astype(np.uint8)).astype(np.float32) / 255.0
# edge strength: difference of gaussians (fine detail) at the cartoon's own scale
fine = cv2.GaussianBlur(g, (0, 0), 1.2) - cv2.GaussianBlur(g, (0, 0), 3.0)
edge = np.clip(-fine * EDGE_GAIN, 0, 1)            # only dark lines, not bright halos
edge = cv2.dilate(edge, np.ones((3, 3), np.uint8))  # thin lines must survive the downscale
dark = np.clip((0.30 - g) / 0.30, 0, 1)            # hair / pupils / outlines
density = TONE_WEIGHT * (1 - g) ** GAMMA + (1 - TONE_WEIGHT) * 0  # soft shading
density = np.clip(density + 1.6 * edge + 0.6 * dark, 0, 1)
density = np.clip((density - FLOOR) / (1 - FLOOR), 0, 1)   # light skin -> blank, lines stay
v = 1.0 - density
 
# ---- 4. character grid
h2, w2 = v.shape
rows = int(COLS * (h2 / w2) * CHAR_ASPECT)
v = cv2.resize(v, (COLS, rows), interpolation=cv2.INTER_AREA)
a = cv2.resize(alpha, (COLS, rows), interpolation=cv2.INTER_AREA)
v = np.where(a < 0.5, 1.0, v)
idx = np.clip(np.round((1.0 - v) * (len(RAMP) - 1)).astype(int), 0, len(RAMP) - 1)
lines = ["".join(RAMP[i] for i in row) for row in idx]
 
open("portrait.txt", "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
print(f"\n{COLS} cols x {rows} rows -> saved portrait.txt")
