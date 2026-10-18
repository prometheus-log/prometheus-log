#!/usr/bin/env python3
"""Render contribution data as a GitHub-style heatmap SVG."""
from pathlib import Path
import json, html
data = json.loads(Path("data/contributions.json").read_text(encoding="utf-8"))
days = data["days"][-371:]
while len(days) % 7:
    days.insert(0, {"date": "", "count": 0, "level": 0})
palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
cell, gap, left, top = 12, 3, 42, 35
cols = len(days)//7
width, height = left+cols*(cell+gap)+18, top+7*(cell+gap)+48
shapes = []
for i, d in enumerate(days):
    x, y = left+(i//7)*(cell+gap), top+(i%7)*(cell+gap)
    level = max(0, min(4, int(d.get("level", 0))))
    title = html.escape(f'{d.get("date","")}: {d.get("count",0)} contributions')
    shapes.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{palette[level]}"><title>{title}</title></rect>')
total = data.get("total", sum(d.get("count", 0) for d in days))
name = html.escape(data.get("username", "GitHub"))
legend = ''.join(f'<rect x="{76+i*15}" y="{height-20}" width="11" height="11" rx="2" fill="{c}"/>' for i,c in enumerate(palette))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" rx="8" fill="#0d1117"/>
<text x="18" y="22" fill="#e6edf3" font-family="monospace" font-size="13">{name} - {total:,} contributions</text>
{''.join(shapes)}<text x="42" y="{height-10}" fill="#8b949e" font-family="monospace" font-size="10">Less</text>{legend}
<text x="160" y="{height-10}" fill="#8b949e" font-family="monospace" font-size="10">More</text></svg>'''
Path("contrib-heatmap.svg").write_text(svg, encoding="utf-8")
print("Wrote contrib-heatmap.svg")

