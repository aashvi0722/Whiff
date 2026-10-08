#!/usr/bin/env python3
"""Run the REAL smoke logic locally against live NASA FIRMS + Open-Meteo.
Set your key for this terminal only (never put it in a file):
    PowerShell:  $env:FIRMS_KEY = "your-key"
    bash:        export FIRMS_KEY=your-key
Usage:  python scripts/try_smoke.py [lat lon]      (default: Delhi)"""
import json, os, sys
from datetime import datetime, timezone

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "backend"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from lib import firms, weather, smoke_logic, festival   # noqa: E402
from check_contract import check_response               # noqa: E402

key = os.environ.get("FIRMS_KEY", "")
if not key:
    sys.exit("FIRMS_KEY is not set in this terminal. See the top of this file.")
lat = float(sys.argv[1]) if len(sys.argv) > 2 else 28.61
lon = float(sys.argv[2]) if len(sys.argv) > 2 else 77.21

now = datetime.now(timezone.utc)
print("1) Fetching FIRMS fire detections (India, last 2 days)...")
fires, errors = firms.fetch_fires(key, now)
print(f"   rows kept (nominal/high confidence): {len(fires)}")
for e in errors:
    print("   source error:", e)
cells = firms.cluster(fires, now)
print(f"   0.25-degree cells with fires: {len(cells)}")
print("   fires in last 24 h by region:", firms.counts_by_region(cells))
age = firms.newest_age_hours(fires, now)
print("   newest detection age (hours):", None if age is None else round(age, 1))

print("2) Fetching wind forecast...")
now_ist = now.astimezone(smoke_logic.IST)
wind = weather.fetch_wind(lat, lon, now_ist.replace(tzinfo=None))
print(f"   {len(wind)} hourly samples; first: {wind[0]}")

print("3) Computing smoke risk...")
res = smoke_logic.build_smoke(lat, lon, festival.city_label(lat, lon), cells, wind, now,
                              0 if age is None else age, festival=festival.festival_for(now_ist.date()))
print(json.dumps(res, indent=2))
problems = check_response("smoke", res)
print("\nContract check:", "OK" if not problems else problems)
