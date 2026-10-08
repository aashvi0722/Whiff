#!/usr/bin/env python3
"""Offline tests for geo / FIRMS parsing / weather parsing / smoke heuristic (fake data, no network).
Run from the repo root:  python scripts/test_smoke_logic.py"""
import json, os, sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "backend"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from lib import geo, firms, weather, smoke_logic as sl      # noqa: E402
from check_contract import check_response                    # noqa: E402

fails = 0
def expect(label, ok, extra=""):
    global fails
    print(("ok   " if ok else "FAIL ") + label + (f"   {extra}" if not ok and extra else ""))
    fails += 0 if ok else 1

IST = timezone(timedelta(hours=5, minutes=30))
NOW = datetime(2026, 10, 9, 6, 0, tzinfo=IST)
DELHI = (28.61, 77.21)

def wind(speed, dir_from, n=24, s850=None):
    return [{"t": f"h{i}", "s10": speed, "d10": dir_from,
             "s850": s850, "d850": dir_from if s850 is not None else None} for i in range(n)]

def cell(lat, lon, n24, nprev=100, region=None):
    return {"lat": lat, "lon": lon, "n24": n24, "nprev": nprev, "frp": 0,
            "region": region or geo.region_code(lat, lon)}

# ---- geo ----
d = geo.haversine_km(28.61, 77.21, 19.07, 72.88)
expect("haversine Delhi-Mumbai about 1150 km", 1100 < d < 1200, d)
expect("bearing due east = 90", abs(geo.bearing_deg(28.61, 74.0, 28.61, 77.21) - 90) < 1.5)
expect("angle_diff wraps (350 vs 10 = 20)", geo.angle_diff(350, 10) == 20)
m, r = geo.circular_mean([350, 10])
expect("circular mean of 350 and 10 is north", (m < 1 or m > 359) and r > 0.98)
expect("cell_center snaps to 0.25 grid", geo.cell_center(28.61, 77.21) == (28.625, 77.125))

# ---- FIRMS parsing ----
HEADER = "latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_ti5,frp,daynight"
CSV = "\n".join([HEADER,
    "30.91,75.85,330.1,0.4,0.37,2026-10-08,1900,N,VIIRS,n,2.0NRT,295.2,5.1,N",   # 5.5 h old, nominal
    "30.92,75.86,340.0,0.4,0.37,2026-10-08,1900,N,VIIRS,h,2.0NRT,295.2,3.0,N",   # high
    "30.93,75.87,320.0,0.4,0.37,2026-10-08,1900,N,VIIRS,l,2.0NRT,295.2,1.0,N",   # low conf -> dropped
    "30.91,75.85,330.1,0.4,0.37,2026-10-07,2330,N,VIIRS,n,2.0NRT,295.2,4.0,N",   # ~30 h old
    "bad,row"])
fires = firms.parse_csv(CSV)
expect("parse keeps nominal/high only, skips bad rows", len(fires) == 3, len(fires))
now_utc = datetime(2026, 10, 9, 6, 0, tzinfo=IST).astimezone(timezone.utc)
cells = firms.cluster(fires, now_utc)
expect("cluster: one cell, 2 recent + 1 previous", len(cells) == 1 and cells[0]["n24"] == 2 and cells[0]["nprev"] == 1, cells)
expect("cluster: Punjab region label", cells[0]["region"] == "IN-PB")
age = firms.newest_age_hours(fires, now_utc)
expect("newest fire age is about 5.5 h", 5 <= age <= 6, age)
try:
    firms.parse_csv("Invalid MAP_KEY.")
    expect("bad key text raises FirmsError", False)
except firms.FirmsError as e:
    expect("bad key text raises FirmsError", True)
expect("URL builder", firms.build_url("K", "VIIRS_SNPP_NRT").endswith("/K/VIIRS_SNPP_NRT/68,6,98,36/2"))
expect("scrub removes the key", "SECRETKEY" not in firms._scrub("url /SECRETKEY/x failed", "SECRETKEY"))

# ---- weather parsing ----
times = [(datetime(2026, 10, 9) + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(72)]
data = {"hourly": {"time": times, "wind_speed_10m": [10.0] * 72, "wind_direction_10m": [270] * 72,
                   "wind_speed_850hPa": [20.0] * 72, "wind_direction_850hPa": [270] * 72}}
w = weather.parse_wind(data, datetime(2026, 10, 9, 6, 30))
expect("wind slice starts at current hour, 48 samples", w[0]["t"] == "2026-10-09T06:00" and len(w) == 48)
w2 = weather.parse_wind({"hourly": {"time": times, "wind_speed_10m": [10.0] * 72, "wind_direction_10m": [270] * 72}},
                        datetime(2026, 10, 9, 6, 30))
expect("missing 850 hPa tolerated", w2[0]["s850"] is None)
try:
    weather.parse_wind({"oops": 1}, datetime(2026, 10, 9, 6))
    expect("bad weather payload raises", False)
except weather.WeatherError:
    expect("bad weather payload raises", True)

# ---- smoke heuristic ----
west = [cell(28.61, 74.0, 400)]                       # ~313 km due west of Delhi
r = sl.build_smoke(*DELHI, "Delhi", west, wind(18, 270), NOW, 3)
expect("west cluster + west wind => high", r["risk"] == "high", r["risk"])
expect("arrival about 17 h and inside its range", 14 <= r["arrival_hours"] <= 20 and r["arrival_range_hours"][0] <= r["arrival_hours"] <= r["arrival_range_hours"][1], r["arrival_hours"])
expect("source bearing points west (about 270)", abs(r["sources"][0]["bearing_deg"] - 270) <= 3, r["sources"])
expect("output validates against the contract", not check_response("smoke", r), check_response("smoke", r))

r = sl.build_smoke(*DELHI, "Delhi", west, wind(18, 90), NOW, 3)
expect("east wind (blowing away) => none", r["risk"] == "none" and r["arrival_hours"] is None)
expect("none response validates + reason codes", not check_response("smoke", r) and r["reason_codes"][0]["code"] == "smoke_none_upwind")

r = sl.build_smoke(*DELHI, "Delhi", west, wind(2, 270), NOW, 3)
expect("calm wind => too slow, none", r["risk"] == "none")
expect("calm wind adds wind_calm_trapping", any(c["code"] == "wind_calm_trapping" for c in r["reason_codes"]))

far = [cell(28.61, 69.0, 400)]                        # ~720 km away, beyond radius
expect("fires beyond 700 km ignored", sl.build_smoke(*DELHI, "Delhi", far, wind(40, 270), NOW, 3)["risk"] == "none")

pb = [cell(30.9, 75.85, 300, nprev=100, region="IN-PB")]
r = sl.build_smoke(*DELHI, "Delhi", pb, wind(18, 330), NOW, 3)
expect("Punjab fires in Oct => crop_residue_likely", r["sources"] and r["sources"][0]["type"] == "crop_residue_likely", r["sources"])
expect("high confidence: steady + rising + <24 h", r["confidence"] == "high", (r["confidence"], r["confidence_reasons"]))
r = sl.build_smoke(*DELHI, "Delhi", pb, wind(18, 330), NOW, 9, stale=True)
expect("stale fire data lowers confidence and flags it", r["confidence"] == "medium" and "fires_stale" in r["confidence_reasons"] and r["data_quality"]["stale"], r["confidence"])
expect("stale adds data_stale code", any(c["code"] == "data_stale" for c in r["reason_codes"]))
nov = datetime(2026, 12, 15, 6, 0, tzinfo=IST)
r = sl.build_smoke(*DELHI, "Delhi", pb, wind(18, 330), nov, 3)
expect("same fires in December => unknown type", r["sources"][0]["type"] == "unknown")
r = sl.build_smoke(*DELHI, "Delhi", west, wind(18, 270), NOW, 3, festival={"active": True, "name": "Diwali"})
expect("festival flag carries through with festival_night code", r["festival"]["active"] and any(c["code"] == "festival_night" for c in r["reason_codes"]) and not check_response("smoke", r))
varying = [{"t": "x", "s10": 18, "d10": (i * 90) % 360, "s850": None, "d850": None} for i in range(24)]
r = sl.build_smoke(*DELHI, "Delhi", west, varying, NOW, 3)
expect("swirling wind => no smoke arrival (net transport ~0)", r["risk"] == "none" and "wind_variable" in r["confidence_reasons"], (r["risk"], r["confidence_reasons"]))
r = sl.build_smoke(*DELHI, "Delhi", [], wind(18, 270), NOW, 0)
expect("no fires at all => none, high confidence", r["risk"] == "none" and r["confidence"] == "high" and "wind_from_clean_sector" in [c["code"] for c in r["reason_codes"]])
r = sl.build_smoke(*DELHI, "Delhi", west, wind(18, 270, s850=30), NOW, 3)
expect("blends 850 hPa wind (speed between 18 and 30)", 18 < r["wind"]["speed_kmh"] < 30, r["wind"])
try:
    sl.build_smoke(*DELHI, "Delhi", west, [], NOW, 3)
    expect("no wind data raises ValueError", False)
except ValueError:
    expect("no wind data raises ValueError", True)

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
