#!/usr/bin/env python3
"""Generate a neofetch-style SVG profile card."""
from pathlib import Path
import os, html
OUT = Path("info-card.svg")
items = [
    ("user", os.getenv("PROFILE_USER", "yourname")),
    ("role", os.getenv("PROFILE_ROLE", "Developer / Student")),
    ("stack", os.getenv("PROFILE_STACK", "Python Â· Django Â· HTML Â· CSS")),
    ("highlights", os.getenv("PROFILE_HIGHLIGHTS", "Building useful things")),
]
groups = []
static = os.getenv("STATIC", "0") == "1"
for i, (key, value) in enumerate(items):
    y = 105 + i*52
    anim = "" if static else f'<animate attributeName="opacity" from="0" to="1" dur=".45s" begin="{.25+i*.35}s" fill="freeze"/>'
    groups.append(f'<g opacity="{1 if static else 0}"><text x="28" y="{y}" class="key">{html.escape(key)}</text><text x="170" y="{y}" class="val">{html.escape(value)}</text>{anim}</g>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="490" height="330" viewBox="0 0 490 330">
<rect x="1" y="1" width="488" height="328" rx="12" fill="#0d1117" stroke="#30363d"/><path d="M1 42H489" stroke="#30363d"/>
<circle cx="22" cy="22" r="5" fill="#ff5f56"/><circle cx="40" cy="22" r="5" fill="#ffbd2e"/><circle cx="58" cy="22" r="5" fill="#27c93f"/>
<text x="80" y="27" fill="#8b949e" font-family="monospace" font-size="13">neofetch - profile</text>
<style>text{{font-family:monospace}} .key{{fill:#7ee787;font-size:16px}} .val{{fill:#e6edf3;font-size:15px}}</style>
{''.join(groups)}<text x="28" y="300" fill="#8b949e" font-family="monospace" font-size="12">$ echo "hello, world"</text></svg>'''
OUT.write_text(svg, encoding="utf-8")
print(f"Wrote {OUT}")

