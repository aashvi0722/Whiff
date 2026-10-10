#!/usr/bin/env python3
"""Offline tests for replay/validation logic and replay serving. Run: python scripts/test_replay_tools.py"""
import json, os, shutil, sys, tempfile
from datetime import datetime, timedelta, timezone, date

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import replay_tools as rt                                    # noqa: E402
from lib import replays, stub                                # noqa: E402
import smoke as smoke_h, day as day_h, replays as replays_h  # noqa: E402
from check_contract import check_response                    # noqa: E402

fails = 0
def expect(label, ok, extra=""):
    global fails
    print(("ok   " if ok else "FAIL ") + label + (f"   {extra}" if not ok and extra else ""))
    fails += 0 if ok else 1

IST = rt.IST
DELHI = {"lat": 28.61, "lon": 77.21, "label": "Delhi"}

# ---- find_jump ----
times = [(datetime(2024, 11, 10) + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(96)]
pm = [50.0] * 48 + [150.0] * 48
t, rule = rt.find_jump(times, pm, "2024-11-10T00:00", "2024-11-14T23:00")
expect("crossing: first hour above 90 after a clean day", t == "2024-11-12T00:00" and rule == "crossing", (t, rule))
pm2 = [120.0] * 48 + [260.0] * 48
t, rule = rt.find_jump(times, pm2, "2024-11-10T00:00", "2024-11-14T23:00")
expect("surge: already poor air, sudden 2x rise", rule == "surge" and t is not None, (t, rule))
t, rule = rt.find_jump(times, [40.0] * 96, "2024-11-10T00:00", "2024-11-14T23:00")
expect("flat series: no jump found", (t, rule) == (None, None))
t, _ = rt.find_jump(times, [None] * 96, "2024-11-10T00:00", "2024-11-14T23:00")
expect("missing data: no crash", t is None)

# ---- spike_time modes and daily summary ----
evt = {"window": ["2024-11-10", "2024-11-11"], "cpcb_target": "2024-11-13T12:00"}
cams_t = {"hourly": {"time": times[:48], "pm2_5": [50.0] * 24 + [150.0] * 24}}
cams_t["hourly"]["time"] = [t.replace("2024-11-1", "2024-11-1") for t in cams_t["hourly"]["time"]]
t_cpcb, how = rt.spike_time(evt, cams_t, "cpcb")
expect("--target cpcb uses the CPCB day", t_cpcb.isoformat().startswith("2024-11-13T12:00") and how == "CPCB date")
t_cams, how = rt.spike_time(evt, cams_t, "cams")
expect("cams mode finds the jump in the series", t_cams.isoformat().startswith("2024-11-11T00:00") and "CAMS" in how, (t_cams, how))
evt2 = {"window": ["2024-11-10", "2024-11-11"], "cpcb_target": "2024-11-13T12:00"}
flat_c = {"hourly": {"time": times[:48], "pm2_5": [40.0] * 48}}
t3, how3 = rt.spike_time(evt2, flat_c, "cams")
expect("flat CAMS series falls back to the CPCB day", t3.isoformat().startswith("2024-11-13T12:00") and "CPCB" in how3)
ds = rt.daily_summary(cams_t, "2024-11-10", "2024-11-11")
expect("daily summary: mean and max per day", ds == [("2024-11-10", 50, 50), ("2024-11-11", 150, 150)], ds)

# ---- simulate: no look-ahead ----
as_of = datetime(2024, 11, 12, 6, 0, tzinfo=IST)
as_of_utc = as_of.astimezone(timezone.utc)
def fire(h_ago, n=1): return [{"lat": 30.9, "lon": 75.85, "frp": 5.0, "t": as_of_utc - timedelta(hours=h_ago)} for _ in range(n)]
wtimes = [(datetime(2024, 11, 11) + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(72)]
wind = {"hourly": {"time": wtimes, "wind_speed_10m": [18.0] * 72, "wind_direction_10m": [330] * 72}}
r_old = rt.simulate(DELHI, fire(8, 300), wind, as_of)
expect("fires 8 h old are used", r_old["risk"] != "none" and r_old["sources"], r_old["risk"])
r_new = rt.simulate(DELHI, fire(1, 300), wind, as_of)
expect("fires newer than the 3 h latency are hidden (no look-ahead)", r_new["risk"] == "none", r_new["risk"])
r_future = rt.simulate(DELHI, fire(-5, 300), wind, as_of)
expect("fires from the future are hidden", r_future["risk"] == "none")
expect("simulate output is contract-valid", not check_response("smoke", r_old) and r_old["data_quality"]["served_from"] == "replay")

# ---- replay files ----
dtimes = [f"2024-11-12T{h:02d}:00" for h in range(24)]
cams = {"hourly": {"time": dtimes, "pm2_5": [40.0] * 24, "pm10": [60.0] * 24}}
ev = {"id": "delhi-2024-11", "label_key": "replay_delhi_2024_11"}
sm, dy = rt.make_replay_files(ev, DELHI, fire(8, 300), wind, cams, as_of)
expect("replay smoke.json: mode, replay block, valid",
       sm["mode"] == "replay" and sm["replay"]["event_id"] == "delhi-2024-11" and sm["generated_at"].startswith("2024-11-12T06:00") and not check_response("smoke", sm))
expect("replay day.json is valid and marked replay", not check_response("day", dy) and dy["date"] == "2024-11-12" and dy["data_quality"]["served_from"] == "replay")

# ---- scoring and threshold sweep ----
sc, n = rt.simulate_score(DELHI, fire(8, 300), wind, as_of)
expect("simulate_score counts the fires and gives a positive score", n == 300 and sc > 0, (sc, n))
sc0, n0 = rt.simulate_score(DELHI, fire(1, 300), wind, as_of)
expect("simulate_score also hides fires newer than the latency", (sc0, n0) == (0, 0))
sw = rt.sweep([10, 50], [5, 20, 40], {"a": {48: 15, 24: 60}, "b": {48: 8, 12: 30}, "c": {6: 999}})
expect("sweep counts calm false alarms", [r["alarms"] for r in sw] == [2, 0], sw)
expect("sweep: events warned only if scored >=12 h ahead", sw[0]["hits"] == {"a": True, "b": True, "c": False} and sw[1]["hits"] == {"a": True, "b": False, "c": False}, sw)

# ---- scoring ----
expect("hit: medium 24 h before => lead 24", rt.evaluate([{"h": 48, "risk": "none"}, {"h": 24, "risk": "medium"}, {"h": 12, "risk": "high"}]) == (True, 24))
expect("miss: only low warnings", rt.evaluate([{"h": 48, "risk": "low"}, {"h": 12, "risk": "low"}]) == (False, None))

# ---- replay serving (temporary replay folder) ----
tmp = tempfile.mkdtemp()
os.makedirs(os.path.join(tmp, "delhi-2024-11"))
json.dump(sm, open(os.path.join(tmp, "delhi-2024-11", "smoke.json"), "w"))
json.dump(dy, open(os.path.join(tmp, "delhi-2024-11", "day.json"), "w"))
old = replays.ROOT; replays.ROOT = tmp
ev_list = replays.list_events()
expect("list_events reads saved replays", len(ev_list) == 1 and ev_list[0]["event_id"] == "delhi-2024-11" and ev_list[0]["city"] == "Delhi")
r = smoke_h.handler({"queryStringParameters": {"replay": "delhi-2024-11"}}, None)
expect("/smoke?replay= serves the saved file", r["statusCode"] == 200 and json.loads(r["body"])["replay"]["event_id"] == "delhi-2024-11")
r = day_h.handler({"queryStringParameters": {"replay": "delhi-2024-11"}}, None)
expect("/day?replay= serves the saved day file", r["statusCode"] == 200 and json.loads(r["body"])["data_quality"]["served_from"] == "replay")
r = smoke_h.handler({"queryStringParameters": {"replay": "nope"}}, None)
expect("unknown replay id -> 404", r["statusCode"] == 404)
r = replays_h.handler({}, None)
b = json.loads(r["body"])
expect("/replays lists the saved events", r["statusCode"] == 200 and b["events"][0]["event_id"] == "delhi-2024-11" and not check_response("replays", b))
for bad in ("../x", "..\\x", "a/b", "", None, "UPPER", "x" * 80):
    expect(f"unsafe replay id rejected: {bad!r}", replays.load(bad, "smoke") is None)
replays.ROOT = old
shutil.rmtree(tmp)
r = replays_h.handler({}, None)
expect("with no saved replays, /replays falls back to the sample list", json.loads(r["body"])["events"] != [])

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
