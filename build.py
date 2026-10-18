"""
build.py  -  terminal-style SVGs for a GitHub profile README (stdlib only)
 
  python build.py portrait          -> portrait.svg   (reads portrait.txt)
  python build.py stack             -> stack.svg      (edit STACK below)
  python build.py stats             -> contrib.svg + stats.svg  (needs token)
  python build.py stats --demo      -> same, with fake data (to preview the look)
 
Token for `stats`: env GITHUB_TOKEN (Actions gives it for free) or GH_TOKEN.
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request
from xml.sax.saxutils import escape
 
# ----------------------------------------------------------------- config
LOGIN = os.environ.get("GH_LOGIN", "prometheus-log")
PROMPT = "prometheus@github"
 
# EDIT THIS: apna asli stack yahan likho
STACK = [
    ("languages", ["Python", "SQL", "HTML", "CSS"]),
    ("backend",   ["Django", "PostgreSQL"]),
    ("tools",     ["Git", "GitHub", "Linux", "VS Code"]),
    ("learning",  ["Redis", "REST APIs"]),
]
 
# ----------------------------------------------------------------- look
FONT = '"JetBrains Mono","SF Mono",Menlo,Consolas,"DejaVu Sans Mono",monospace'
BG, BAR, LINE = "#0d1117", "#161b22", "#30363d"
FG, DIM, GREEN = "#e6edf3", "#7d8590", "#39d353"
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
HALF_W = 814      # two of these sit side by side (displayed at width=410)
FULL_W = 1660     # full width (displayed at width=830)
ANIM = os.environ.get("NOANIM") != "1"
 
 
def window(w, h, title, inner, defs=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family='{FONT}'>
<defs><clipPath id="win"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14"/></clipPath>{defs}</defs>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="{BG}" stroke="{LINE}" stroke-width="2"/>
<g clip-path="url(#win)"><rect x="0" y="0" width="{w}" height="52" fill="{BAR}"/></g>
<circle cx="30" cy="26" r="8" fill="#ff5f56"/><circle cx="58" cy="26" r="8" fill="#ffbd2e"/><circle cx="86" cy="26" r="8" fill="#27c93f"/>
<text x="{w/2}" y="32" text-anchor="middle" font-size="20" fill="{DIM}">{escape(title)}</text>
{inner}
</svg>"""
 
 
def write(name, svg):
    with open(name, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {name} ({len(svg)//1024 or 1} KB)")
 
 
# ----------------------------------------------------------------- portrait
def portrait():
    lines = open("portrait.txt", encoding="utf-8").read().split("\n")
    cols = max(len(l) for l in lines)
    pad = 30
    cw = (HALF_W - 2 * pad) / cols          # width of one character
    fs, lh = cw / 0.6, cw / 0.48
    x0 = (HALF_W - cw * cols) / 2
    top = 52 + pad
    h = int(top + len(lines) * lh + pad + 44)
    row_delay, row_dur = 0.09, 0.45
 
    defs, body = [], []
    for i, line in enumerate(lines):
        s = line.rstrip()
        if not s.strip():
            continue
        lead = len(s) - len(s.lstrip())
        s = s.lstrip()
        xs = round(x0 + lead * cw, 2)
        wid = round(len(s) * cw, 2)
        y = round(top + i * lh, 2)
        t0 = round(i * row_delay, 2)
        t1 = round(t0 + row_dur, 2)
        start_w = 0 if ANIM else wid
        anim = (f'<animate attributeName="width" from="0" to="{wid}" dur="{row_dur}s" begin="{t0}s" fill="freeze"/>'
                if ANIM else "")
        defs.append(f'<clipPath id="r{i}"><rect x="{xs}" y="{y}" width="{start_w}" height="{round(lh+1,2)}">{anim}</rect></clipPath>')
        body.append(
            f'<text x="{xs}" y="{round(y + fs, 2)}" textLength="{wid}" lengthAdjust="spacing" '
            f'font-size="{round(fs,2)}" fill="#c9d1d9" xml:space="preserve" clip-path="url(#r{i})">{escape(s)}</text>')
        if ANIM:
            body.append(
                f'<rect y="{y+1}" width="{round(cw,2)}" height="{round(lh-2,2)}" fill="{GREEN}" opacity="0">'
                f'<set attributeName="opacity" to="1" begin="{t0}s"/>'
                f'<animate attributeName="x" from="{xs}" to="{round(xs+wid,2)}" dur="{row_dur}s" begin="{t0}s" fill="freeze"/>'
                f'<set attributeName="opacity" to="0" begin="{t1}s"/></rect>')
    foot = (f'<text x="30" y="{h-26}" font-size="20" fill="{DIM}">{PROMPT}:~$ whoami  '
            f'<tspan fill="{FG}" font-weight="bold">{escape(LOGIN)}</tspan></text>')
    write("portrait.svg", window(HALF_W, h, f"{PROMPT}: ~ $ ./portrait.sh",
                                 "".join(body) + foot, "".join(defs)))
    return h
 
 
# ----------------------------------------------------------------- stack
def stack():
    rows = len(STACK)
    h = 52 + 40 + 70 + rows * 80 + 24
    out = [f'<text x="40" y="{52+62}" font-size="28" fill="{FG}"><tspan fill="{GREEN}">$</tspan> cat stack.txt</text>']
    y = 52 + 70 + 30
    for label, items in STACK:
        out.append(f'<text x="40" y="{y+32}" font-size="26" fill="{DIM}">{escape(label)}</text>')
        x = 300
        for it in items:
            w = len(it) * 15.6 + 44
            out.append(
                f'<rect x="{x}" y="{y}" width="{w:.0f}" height="48" rx="10" fill="{BAR}" stroke="{LINE}" stroke-width="2"/>'
                f'<text x="{x + w/2:.0f}" y="{y+32}" text-anchor="middle" font-size="25" fill="{FG}">{escape(it)}</text>')
            x += w + 16
        y += 80
    write("stack.svg", window(FULL_W, h, f"{PROMPT}: ~ $ ./stack.sh", "".join(out)))
 
 
# ----------------------------------------------------------------- data
def fetch():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN / GH_TOKEN set nahi hai. Preview ke liye: python build.py stats --demo")
    today = dt.datetime.now(dt.timezone.utc).date()
    start = today - dt.timedelta(days=364)
    q = """query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){
      contributionsCollection(from:$from,to:$to){contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
    payload = {"query": q, "variables": {"login": LOGIN, "from": f"{start}T00:00:00Z", "to": f"{today}T23:59:59Z"}}
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=json.dumps(payload).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-kit"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in data:
        sys.exit(f"GitHub API error: {data['errors']}")
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [(dt.date.fromisoformat(d["date"]), d["contributionCount"]) for w in weeks for d in w["contributionDays"]]
    return sorted(days)
 
 
def demo_days():
    rnd = random.Random(7)
    today = dt.date.today()
    out = []
    for i in range(365):
        d = today - dt.timedelta(days=364 - i)
        out.append((d, 0 if rnd.random() < 0.25 else int(rnd.expovariate(1 / 6))))
    return out
 
 
def analyse(days):
    total = sum(c for _, c in days)
    active = sum(1 for _, c in days if c > 0)
    # current streak: today may still be empty, so start from yesterday then
    i = len(days) - 1
    if days[i][1] == 0:
        i -= 1
    cur_end = days[i][0] if i >= 0 else None
    cur = 0
    while i >= 0 and days[i][1] > 0:
        cur += 1
        i -= 1
    cur_start = days[i + 1][0] if cur else None
    # longest streak
    best, run, run_start, best_range = 0, 0, None, (None, None)
    for d, c in days:
        if c > 0:
            run_start = run_start or d
            run += 1
            if run > best:
                best, best_range = run, (run_start, d)
        else:
            run, run_start = 0, None
    bd = max(days, key=lambda x: x[1])
    months = {}
    for d, c in days:
        months[(d.year, d.month)] = months.get((d.year, d.month), 0) + c
    return dict(total=total, active=active, n=len(days), cur=cur, cur_range=(cur_start, cur_end),
                longest=best, long_range=best_range, best_day=bd, avg=total / active if active else 0,
                months=months)
 
 
def fmt(d):
    return d.strftime("%b ") + str(d.day) if d else "-"
 
 
# ----------------------------------------------------------------- contributions heatmap
def contrib(days):
    left = 70
    first = days[0][0]
    sunday0 = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    ncols = (days[-1][0] - sunday0).days // 7 + 1
    pitch = (FULL_W - left - 40) / ncols
    cell = pitch - 5
    nz = sorted(c for _, c in days if c > 0)
    q = [nz[int(len(nz) * p)] for p in (0.25, 0.5, 0.75)] if nz else [1, 2, 3]
 
    def level(c):
        return 0 if c == 0 else 1 + sum(c > t for t in q)
 
    top = 52 + 70
    out, seen_month = [], None
    for d, c in days:
        col = (d - sunday0).days // 7
        row = (d.weekday() + 1) % 7
        x, y = left + col * pitch, top + row * pitch
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="4" fill="{LEVELS[level(c)]}"/>')
        if row == 0 and d.month != seen_month:
            seen_month = d.month
            out.append(f'<text x="{x:.1f}" y="{top-14}" font-size="21" fill="{DIM}">{d.strftime("%b")}</text>')
    for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="14" y="{top + r*pitch + 20}" font-size="21" fill="{DIM}">{name}</text>')
    total = sum(c for _, c in days)
    h = top + 7 * pitch + 70
    out.append(f'<text x="{left}" y="{h-26}" font-size="28" font-weight="bold" fill="{FG}">{total:,} contributions in the last year</text>')
    write("contrib.svg", window(FULL_W, h, f"{PROMPT}: ~ $ ./contributions.sh", "".join(out)))
 
 
# ----------------------------------------------------------------- stats cards
def card(x, y, w, h, label, value, unit, sub, color=FG):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{BAR}" stroke="{LINE}" stroke-width="2"/>'
            f'<text x="{x+24}" y="{y+38}" font-size="21" fill="{DIM}">$ {escape(label)}</text>'
            f'<text x="{x+24}" y="{y+102}" font-size="62" font-weight="bold" fill="{color}">{escape(value)}'
            f'<tspan font-size="22" font-weight="normal" fill="{DIM}" dx="10">{escape(unit)}</tspan></text>'
            f'<text x="{x+24}" y="{y+134}" font-size="20" fill="{DIM}">{escape(sub)}</text>')
 
 
def stats(days, H):
    a = analyse(days)
    pad, gap, ch = 24, 20, 150
    cw = (HALF_W - 2 * pad - gap) // 2
    x1, x2, y = pad, pad + cw + gap, 52 + pad
    cur_sub = f"{fmt(a['cur_range'][0])} - {fmt(a['cur_range'][1])}" if a["cur"] else "start one today"
    lo, hi = a["long_range"]
    out = [
        card(x1, y, cw, ch, "current streak", str(a["cur"]), "days", cur_sub, GREEN),
        card(x2, y, cw, ch, "longest streak", str(a["longest"]), "days", f"{fmt(lo)} - {fmt(hi)}"),
        card(x1, y + ch + gap, cw, ch, "contributions", f"{a['total']:,}", "", "in the last year"),
        card(x2, y + ch + gap, cw, ch, "active days", str(a["active"]), f"/ {a['n']}", f"{100*a['active']//a['n']}% of the year"),
        card(x1, y + 2 * (ch + gap), cw, ch, "best day", str(a["best_day"][1]), "", fmt(a["best_day"][0])),
        card(x2, y + 2 * (ch + gap), cw, ch, "avg / active day", f"{a['avg']:.1f}", "", "contributions"),
    ]
    cy = y + 3 * (ch + gap)
    chh = max(200, H - cy - pad)
    out.append(f'<rect x="{pad}" y="{cy}" width="{HALF_W-2*pad}" height="{chh}" rx="12" fill="{BAR}" stroke="{LINE}" stroke-width="2"/>')
    out.append(f'<text x="{pad+24}" y="{cy+38}" font-size="21" fill="{DIM}">$ contributions / month</text>')
    items = list(a["months"].items())
    mx = max(v for _, v in items) or 1
    inner_w = HALF_W - 2 * pad - 48
    slot = inner_w / len(items)
    base = cy + chh - 44
    area = base - (cy + 80)
    for k, ((yr, mo), v) in enumerate(items):
        bh = max(4, area * v / mx) if v else 4
        bx = pad + 24 + k * slot + slot * 0.18
        col = GREEN if v == mx else "#26a641"
        out.append(f'<rect x="{bx:.1f}" y="{base-bh:.1f}" width="{slot*0.64:.1f}" height="{bh:.1f}" rx="4" fill="{col}"/>')
        out.append(f'<text x="{bx+slot*0.32:.1f}" y="{base+30}" text-anchor="middle" font-size="19" fill="{DIM}">{dt.date(yr, mo, 1).strftime("%b")[0]}</text>')
        if v == mx:
            out.append(f'<text x="{bx+slot*0.32:.1f}" y="{base-bh-10:.1f}" text-anchor="middle" font-size="19" fill="{FG}">{v:,}</text>')
    write("stats.svg", window(HALF_W, H, f"{PROMPT}: ~ $ ./stats.sh", "".join(out)))
 
 
def portrait_height():
    """stats window should match the portrait window height"""
    try:
        lines = open("portrait.txt", encoding="utf-8").read().split("\n")
        cols = max(len(l) for l in lines)
        cw = (HALF_W - 60) / cols
        return int(52 + 30 + len(lines) * cw / 0.48 + 30 + 44)
    except FileNotFoundError:
        return 880
 
 
# ----------------------------------------------------------------- main
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "portrait":
        portrait()
    elif cmd == "stack":
        stack()
    elif cmd == "stats":
        d = demo_days() if "--demo" in sys.argv else fetch()
        contrib(d)
        stats(d, max(portrait_height(), 800))
    else:
        sys.exit(__doc__)
 
