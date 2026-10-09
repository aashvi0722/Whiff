#!/usr/bin/env python3
"""Offline tests for AQI bands and /day window logic (the playbook's six cases plus extras).
Run from the repo root:  python scripts/test_day_logic.py"""
import json, os, sys
from datetime import date, datetime, timezone

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "backend"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from lib import bands, day_logic, weather    # noqa: E402
import day as day_handler                    # noqa: E402
from check_contract import check_response    # noqa: E402

fails = 0
def expect(label, ok, extra=""):
    global fails
    print(("ok   " if ok else "FAIL ") + label + (f"   {extra}" if not ok and extra else ""))
    fails += 0 if ok else 1

LOC = {"lat": 28.61, "lon": 77.21, "label": "Delhi"}
def day(pm_by_h, aud="general", **kw):
    return day_logic.build_day({h: (v, None) for h, v in pm_by_h.items()}, aud, "2026-10-09", LOC, **kw)
def flat(v, hours=range(5, 23)): return {h: v for h in hours}
def win(d): return [(w["start_h"], w["end_h"]) for w in d["windows"]]

# ---- AQI conversion (CPCB breakpoints) ----
for pm, want in [(0, 0), (30, 50), (60, 100), (90, 200), (120, 300), (250, 400)]:
    expect(f"PM2.5 {pm} -> AQI {want}", bands.aqi_from(pm) == want, bands.aqi_from(pm))
expect("PM10 100 -> 100, 250 -> 200", bands.aqi_from(0, 100) == 100 and bands.aqi_from(0, 250) == 200)
expect("AQI is the larger sub-index (pm25 20, pm10 250 -> 200)", bands.aqi_from(20, 250) == 200)
expect("PM10 missing is fine", bands.aqi_from(45, None) == bands.aqi_from(45))
expect("very high PM2.5 caps at 500", bands.aqi_from(900) == 500)
expect("bands", [bands.band_of(a) for a in (50, 100, 200, 300, 400, 401)] == ["good", "satisfactory", "moderate", "poor", "very_poor", "severe"])

# ---- the playbook's six cases ----
d = day(flat(20))
expect("1. all hours 20 -> windows, one long window 5-21", d["day_state"] == "windows" and win(d) == [(5, 21)], win(d))
p = flat(80); p.update({6: 25, 7: 25, 8: 25})
d = day(p)
expect("2. dip 25 at 6-8, else 80 -> window 6-8 ranked first", win(d)[0] == (6, 8) and d["windows"][0]["rank"] == 1, win(d))
d = day(flat(150))
expect("3. all hours 150 -> stay_in, no windows", d["day_state"] == "stay_in" and d["windows"] == [] and d["reason_codes"][0]["code"] == "all_day_poor")
p = flat(80); p.update({6: 40, 7: 40, 8: 40})
expect("4. dip 40: general gets a window, sensitive (stricter) gets none",
       win(day(p)) == [(6, 8)] and day(p, "sensitive")["windows"] == [] and day(p, "sensitive")["day_state"] == "caution")
p = flat(80); p.update({6: 30, 7: 30, 8: 30, 14: 30, 15: 30})
d = day(p)
expect("5. equal depth, different length -> longer ranked first", win(d)[:2] == [(6, 8), (14, 15)], win(d))
p = flat(20); del p[9]; del p[10]
d = day(p)
expect("6. missing hours: no crash, gaps skipped, noted", d["data_quality"]["missing_hours"] == 2 and win(d) == [(11, 21), (5, 8)] and not check_response("day", d), win(d))

# ---- extras ----
d = day(flat(20)); expect("hours cover 5..22", [h["h"] for h in d["hours"]] == list(range(5, 23)))
p = flat(80); p.update({6: 25, 7: 25, 8: 25})
d = day(p)
expect("summary fields (best/worst/avoided/cigarettes)", d["best_hour"] == 6 and d["exposure_avoided_hours"] == 14 and d["cigarette_equiv"]["approx"] is True, d["exposure_avoided_hours"])
expect("window reason: pm25_below_avg with a percent", d["windows"][0]["reason_codes"][0]["code"] == "pm25_below_avg" and d["windows"][0]["reason_codes"][0]["params"]["percent"] > 0)
d = day(p, wake_h=7)
expect("wake_h=7 trims the window to 7-8", win(d) == [(7, 8)], win(d))
d = day(flat(150), "outdoor")
expect("outdoor never gets stay_in; caution + shift_heavy_work", d["day_state"] == "caution" and "shift_heavy_work" in d["advice_codes"] and not check_response("day", d))
d = day(flat(150))
expect("stay_in advice includes indoor_swap and run_purifier", {"indoor_swap", "run_purifier"} <= set(d["advice_codes"]))
d = day(flat(20)); expect("clean day has no advice codes", d["advice_codes"] == [], d["advice_codes"])
expect("child stricter than general", day(dict(flat(70)), "general")["day_state"] == "caution" and bands.status_for(90, "child") == "caution" and bands.status_for(90, "general") == "go")
expect("unknown audience falls back to general", day(flat(20), "wizard")["audience"] == "general")
expect("outputs validate against contract", all(not check_response("day", day(x)) for x in (flat(20), flat(80), flat(150))))
for bad in ({}, {h: (None, None) for h in range(5, 23)}):
    try:
        day_logic.build_day(bad, "general", "2026-10-09", LOC); expect("empty data raises ValueError", False)
    except ValueError:
        expect("empty data raises ValueError", True)

# ---- air-quality parsing ----
times = [f"2026-10-09T{h:02d}:00" for h in range(24)] + [f"2026-10-10T{h:02d}:00" for h in range(3)]
aq = {"hourly": {"time": times, "pm2_5": [10.5] * 27, "pm10": [20.0] * 26 + [None]}}
got = weather.parse_air_quality(aq, date(2026, 10, 9))
expect("AQ parse keeps only today's 24 hours", sorted(got) == list(range(24)) and got[6] == (10.5, 20.0))
try:
    weather.parse_air_quality({"hourly": {}}, date(2026, 10, 9)); expect("bad AQ payload raises", False)
except weather.WeatherError:
    expect("bad AQ payload raises", True)

# ---- handler wiring (network replaced by a fake) ----
day_handler._hourly = lambda lat, lon, d: ({h: (20.0, 30.0) for h in range(24)}, "live")
r = day_handler.handler({"queryStringParameters": {"lat": "28.61", "lon": "77.21", "audience": "child", "wake_h": "7"}}, None)
b = json.loads(r["body"])
expect("handler returns a valid /day body", r["statusCode"] == 200 and b["audience"] == "child" and not check_response("day", b))
def boom(*a): raise RuntimeError("x")
day_handler._hourly = boom
r = day_handler.handler({"queryStringParameters": {"lat": "28.61", "lon": "77.21"}}, None)
expect("handler: upstream failure -> 503 error shape", r["statusCode"] == 503 and json.loads(r["body"])["error"]["code"] == "upstream_unavailable")

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
