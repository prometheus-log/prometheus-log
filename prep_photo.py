#!/usr/bin/env python3
"""Prepare a photo: remove background where possible, enhance contrast, output grayscale."""
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageOps, ImageEnhance

if len(sys.argv) < 2:
    raise SystemExit("Usage: python scripts/prep_photo.py portrait.jpg [source-prepped.png]")
src = Path(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("source-prepped.png")
image = Image.open(src).convert("RGBA")
try:
    from rembg import remove
    image = remove(image).convert("RGBA")
    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    image = Image.alpha_composite(white, image).convert("RGB")
except Exception as exc:
    print(f"Background removal unavailable; using original background: {exc}")
    image = image.convert("RGB")
gray = ImageOps.grayscale(image)
try:
    import cv2
    gray = Image.fromarray(cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(np.array(gray)))
except Exception:
    gray = ImageEnhance.Contrast(ImageOps.autocontrast(gray, cutoff=1)).enhance(1.25)
ImageEnhance.Sharpness(gray).enhance(1.4).save(out)
print(f"Wrote {out}")

