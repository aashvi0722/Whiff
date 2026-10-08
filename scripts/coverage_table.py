#!/usr/bin/env python3
"""Data coverage table: for each test city, count missing hours in the Open-Meteo wind and PM2.5 data.
    python scripts/coverage_table.py            # print the markdown table
    python scripts/coverage_table.py --write    # also write it into docs/architecture.md"""
import json, os, sys
from datetime import datetime, timezone

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "backend"))
from lib import weather, smoke_logic   # noqa: E402

cities = json.load(open(os.path.join(ROOT, "backend", "config", "cities.json"), encoding="utf-8"))["cities"]
now_ist = datetime.now(timezone.utc).astimezone(smoke_logic.IST).replace(tzinfo=None)
rows = ["| City | Wind ok? | PM2.5 ok? | Notes |", "|---|---|---|---|"]
for c in cities:
    wind_ok = pm_ok = "ERROR"
    notes = []
    try:
        w = weather.fetch_wind(c["lat"], c["lon"], now_ist, hours=48)
        miss10 = sum(1 for s in w if s["s10"] is None or s["d10"] is None)
        miss850 = sum(1 for s in w if s["s850"] is None or s["d850"] is None)
        wind_ok = "yes" if miss10 == 0 else f"no ({miss10}/{len(w)} h missing)"
        if miss850:
            notes.append(f"850 hPa wind missing {miss850}/{len(w)} h (10 m used)")
    except Exception as e:
        notes.append(f"wind: {type(e).__name__}")
    try:
        d = weather.fetch_json(weather.air_quality_url(c["lat"], c["lon"]))["hourly"]
        vals = d["pm2_5"]
        miss = sum(1 for v in vals if v is None)
        pm_ok = "yes" if miss == 0 else f"partial ({miss}/{len(vals)} h missing)"
        if miss == len(vals):
            pm_ok = "no (all missing)"
    except Exception as e:
        notes.append(f"pm2.5: {type(e).__name__}")
    rows.append(f"| {c['label']} | {wind_ok} | {pm_ok} | {'; '.join(notes) or '-'} |")
table = "\n".join(rows)
print(table)

if "--write" in sys.argv:
    path = os.path.join(ROOT, "docs", "architecture.md")
    text = open(path, encoding="utf-8").read()
    a, b = "<!-- coverage:start -->", "<!-- coverage:end -->"
    if a in text and b in text:
        text = text[:text.index(a) + len(a)] + "\n" + table + "\n" + text[text.index(b):]
        open(path, "w", encoding="utf-8").write(text)
        print("\nwritten to docs/architecture.md")
    else:
        print("\nmarkers not found in docs/architecture.md; paste the table by hand")
