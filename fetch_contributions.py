#!/usr/bin/env python3
"""Fetch the public GitHub contribution calendar without a token."""
from pathlib import Path
import os, json, datetime, requests
from bs4 import BeautifulSoup

user = os.getenv("GITHUB_USERNAME", "yourname")
if user == "yourname":
    raise SystemExit("Set GITHUB_USERNAME to your GitHub username.")
url = f"https://github.com/users/{user}/contributions"
r = requests.get(url, timeout=30, headers={"User-Agent": "profile-art-generator"})
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")
cells = soup.select("td.ContributionCalendar-day") or soup.select("[data-date][data-level]")
days = []
for cell in cells:
    date = cell.get("data-date")
    if not date:
        continue
    try: count = int(cell.get("data-count") or 0)
    except ValueError: count = 0
    try: level = int(cell.get("data-level") or 0)
    except ValueError: level = 0
    days.append({"date": date, "count": count, "level": max(0, min(4, level))})
if not days:
    raise SystemExit("No contribution cells found; GitHub may have changed its HTML.")
payload = {"username": user, "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "total": sum(d["count"] for d in days), "days": days}
Path("data").mkdir(exist_ok=True)
Path("data/contributions.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"Saved {len(days)} days for {user}")

