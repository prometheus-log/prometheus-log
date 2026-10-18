#!/usr/bin/env python3
"""Turn source-prepped.png into a monochrome ASCII portrait SVG with row reveal animation."""
from pathlib import Path
from PIL import Image
import html, os

INPUT = Path(os.getenv("ASCII_INPUT", "source-prepped.png"))
OUTPUT = Path(os.getenv("ASCII_OUTPUT", "avi-ascii.svg"))
COLS = int(os.getenv("ASCII_COLS", "100"))
RAMP = " .`:-=+*cs#%@"
CELL_W, CELL_H = 8, 12

def main():
    if not INPUT.exists():
        raise SystemExit(f"Missing {INPUT}; run scripts/prep_photo.py portrait.jpg first.")
    img = Image.open(INPUT).convert("L")
    rows = max(1, round(COLS * img.height / img.width * 0.50))
    img = img.resize((COLS, rows), Image.Resampling.LANCZOS)
    pix = list(img.getdata())
    lines = []
    for y in range(rows):
        line = ""
        for x in range(COLS):
            brightness = pix[y*COLS+x] / 255
            idx = min(len(RAMP)-1, int((1-brightness)*(len(RAMP)-1)))
            line += RAMP[idx]
        lines.append(line.rstrip())
    width, height = COLS*CELL_W+24, rows*CELL_H+24
    parts = []
    for i, line in enumerate(lines):
        y = 18+(i+1)*CELL_H
        parts.append(f'<clipPath id="c{i}"><rect x="12" y="{y-CELL_H+1}" width="0" height="{CELL_H+1}"><animate attributeName="width" from="0" to="{COLS*CELL_W}" dur=".75s" begin="{i*.035:.3f}s" fill="freeze"/></rect></clipPath><text x="12" y="{y}" clip-path="url(#c{i})">{html.escape(line)}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<title>Animated monochrome ASCII portrait</title><rect width="100%" height="100%" fill="#ffffff"/>
<style>text{{font:{CELL_H}px monospace;fill:#222;white-space:pre}}</style>{''.join(parts)}</svg>'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({COLS} x {rows} characters)")
if __name__ == "__main__":
    main()

