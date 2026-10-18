from xml.sax.saxutils import escape

CHAR_W = 7.74      # 0.600 em at font-size 12.9
FONT_SIZE = 12.9
LINE_H = 15.5
ROW_DELAY = 0.09   # stagger between rows
ROW_DUR = 0.45     # time to type one row

lines = open("portrait.txt", encoding="utf-8").read().split("\n")
cols = max(len(l) for l in lines)
W = round(cols * CHAR_W, 2)
H = round(len(lines) * LINE_H + 8, 2)

defs, body = [], []
for i, line in enumerate(lines):
    y = round(i * LINE_H, 2)
    t0 = round(i * ROW_DELAY, 2)
    t1 = round(t0 + ROW_DUR, 2)

    defs.append(
        f'<clipPath id="c{i}"><rect x="0" y="{y}" width="0" height="{LINE_H}">'
        f'<animate attributeName="width" from="0" to="{W}" dur="{ROW_DUR}s" '
        f'begin="{t0}s" fill="freeze"/></rect></clipPath>'
    )
    body.append(
        f'<text x="0" y="{round(y + FONT_SIZE, 2)}" clip-path="url(#c{i})" '
        f'xml:space="preserve">{escape(line)}</text>'
    )
    # cursor block riding the wipe edge
    body.append(
        f'<rect class="cur" y="{y + 1}" width="{CHAR_W}" height="{LINE_H - 2}" opacity="0">'
        f'<set attributeName="opacity" to="1" begin="{t0}s"/>'
        f'<animate attributeName="x" from="0" to="{W}" dur="{ROW_DUR}s" begin="{t0}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0" begin="{t1}s"/></rect>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
  text {{ font-family: "JetBrains Mono","DejaVu Sans Mono","Liberation Mono",Consolas,monospace; font-size: {FONT_SIZE}px; fill: #1f2328; }}
  .cur {{ fill: #1f2328; }}
  @media (prefers-color-scheme: dark) {{ text, .cur {{ fill: #e6edf3; }} }}
</style>
<defs>{"".join(defs)}</defs>
{"".join(body)}
</svg>'''

open("portrait.svg", "w", encoding="utf-8").write(svg)
print(f"portrait.svg written: {cols} cols x {len(lines)} rows")