#!/usr/bin/env python3
"""Offline tests: cache layer, cache-first service, stale-on-failure, hourly ingest (all upstreams faked).
Run from the repo root:  python scripts/test_ingest_cache.py"""
import json, os, sys
from datetime import datetime, timezone, timedelta, date

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "backend"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from lib import cache as cm, service, firms, weather, smoke_logic   # noqa: E402
import ingest, smoke, day as day_handler                            # noqa: E402
from check_contract import check_response                           # noqa: E402

fails = 0
def expect(label, ok, extra=""):
    global fails
    print(("ok   " if ok else "FAIL ") + label + (f"   {extra}" if not ok and extra else ""))
    fails += 0 if ok else 1

IST = timezone(timedelta(hours=5, minutes=30))
NOW = datetime(2026, 10, 9, 11, 0, tzinfo=IST).astimezone(timezone.utc)

# ---- fakes for the two upstreams, with call counters ----
calls = {"firms": 0, "wind": 0, "aq": 0}
state = {"firms_down": False, "weather_down": False}
def fake_fires(key, now=None, **kw):
    calls["firms"] += 1
    if state["firms_down"]:
        raise firms.FirmsError("down")
    t = NOW - timedelta(hours=3)
    return ([{"lat": 30.9, "lon": 75.85, "frp": 5.0, "t": t}] * 300 + [{"lat": 28.7, "lon": 74.2, "frp": 3.0, "t": t}] * 50), []
def fake_wind(lat, lon, now_ist_naive, hours=48, timeout=8):
    calls["wind"] += 1
    if state["weather_down"]:
        raise weather.WeatherError("down")
    return [{"t": "x", "s10": 18, "d10": 330, "s850": None, "d850": None} for _ in range(24)]
def fake_json(url, timeout=8):
    calls["aq"] += 1
    if state["weather_down"]:
        raise weather.WeatherError("down")
    days = sorted({date(2026, 10, 9), datetime.now(IST).date()})   # the fixed test date and the real "today" the ingest asks for
    times = [f"{d.isoformat()}T{h:02d}:00" for d in days for h in range(24)]
    return {"hourly": {"time": times, "pm2_5": [40.0] * len(times), "pm10": [60.0] * len(times)}}
firms.fetch_fires, weather.fetch_wind, weather.fetch_json = fake_fires, fake_wind, fake_json

def reset():
    for k in calls: calls[k] = 0
    state.update(firms_down=False, weather_down=False)
    c = cm.MemoryCache(); cm._singleton["c"] = c
    return c

# ---- cache layer ----
c = cm.MemoryCache()
cm.write(c, "a", {"x": 1}, 60, now=1000)
expect("write then read is fresh", cm.read(c, "a", now=1030) == ({"x": 1}, True))
expect("expired item is still returned, marked not fresh", cm.read(c, "a", now=1100) == ({"x": 1}, False))
expect("ttl (cleanup) is later than exp (fresh until)", c.items["a"]["ttl"] > c.items["a"]["exp"])
expect("miss returns (None, False)", cm.read(c, "nope") == (None, False))
big = {"cells": [[28.0 + i * 0.001, 77.0, 5, 3, 12.5, "IN"] for i in range(9000)]}
enc = cm.encode(big)
expect("large value is gzip+base64 and far below DynamoDB's 400 KB limit", enc.startswith("gz:") and len(enc) < 150_000, len(enc))
expect("gzip roundtrip is lossless", cm.decode(enc) == big)
class Broken:
    def get(self, pk): raise RuntimeError("boom")
    def put(self, pk, item): raise RuntimeError("boom")
expect("cache errors never raise (read)", cm.read(Broken(), "a") == (None, False))
expect("cache errors never raise (write)", cm.write(Broken(), "a", {}, 10) is False)
expect("no cache object at all is fine", cm.read(None, "a") == (None, False) and cm.write(None, "a", {}, 1) is False)

# ---- fires: cache-first, stale-on-failure ----
c = reset()
cells, newest, src, stale = service.get_fires(c, "K", NOW)
expect("first call fetches FIRMS and stores the snapshot", src == "live" and calls["firms"] == 1 and "fires#latest" in c.items and len(cells) == 2)
expect("newest detection time is kept", newest is not None and abs((NOW - newest).total_seconds() / 3600 - 3) < 0.01)
cells2, _, src2, _ = service.get_fires(c, "K", NOW)
expect("second call is served from cache, FIRMS not called again", src2 == "cache" and calls["firms"] == 1 and cells2 == cells)
c.items["fires#latest"]["exp"] = 0; state["firms_down"] = True
_, _, src3, stale3 = service.get_fires(c, "K", NOW)
expect("expired snapshot + FIRMS down => stale snapshot served", src3 == "cache" and stale3 is True)
c2 = reset(); state["firms_down"] = True
try:
    service.get_fires(c2, "K", NOW); expect("no snapshot + FIRMS down raises", False)
except firms.FirmsError:
    expect("no snapshot + FIRMS down raises", True)

# ---- smoke: cache-first, localised, stale fallback ----
c = reset()
r1 = service.compute_smoke(28.61, 77.21, NOW, c, "K")
expect("first /smoke computes live and is contract-valid", r1["data_quality"]["served_from"] == "live" and not check_response("smoke", r1), r1["data_quality"])
expect("result stored under a 0.25 degree grid key", any(k.startswith("smoke#28.625#77.125") for k in c.items))
w0 = calls["wind"]
r2 = service.compute_smoke(28.62, 77.20, NOW, c, "K")
expect("second /smoke (same grid cell) comes from cache, no new wind call", r2["data_quality"]["served_from"] == "cache" and calls["wind"] == w0)
expect("cached result is localised to the caller's coordinates", r2["location"]["lat"] == 28.62 and r2["location"]["lon"] == 77.2)
for k in c.items: c.items[k]["exp"] = 0
state["weather_down"] = True
r3 = service.compute_smoke(28.61, 77.21, NOW, c, "K")
expect("expired + upstream down => stale result, flagged, with data_stale code",
       r3["data_quality"]["stale"] is True and any(x["code"] == "data_stale" for x in r3["reason_codes"]) and not check_response("smoke", r3))
try:
    service.compute_smoke(12.97, 77.59, NOW, c, "K"); expect("nothing cached + upstream down raises", False)
except Exception:
    expect("nothing cached + upstream down raises", True)

# ---- air quality for /day ----
c = reset()
h1, s1 = service.get_hourly(c, 28.61, 77.21, date(2026, 10, 9))
h2, s2 = service.get_hourly(c, 28.61, 77.21, date(2026, 10, 9))
expect("air quality: live then cache, one upstream call", (s1, s2) == ("live", "cache") and calls["aq"] == 1 and h1 == h2)
for k in c.items: c.items[k]["exp"] = 0
state["weather_down"] = True
h3, s3 = service.get_hourly(c, 28.61, 77.21, date(2026, 10, 9))
expect("air quality: expired + upstream down => stale", s3 == "stale" and h3 == h1)
day_handler._hourly = lambda lat, lon, d: service.get_hourly(c, lat, lon, d)
r = day_handler.compute_day(28.61, 77.21, "general", None, NOW)
expect("/day built from stale data is flagged stale and valid", r["data_quality"]["stale"] is True and not check_response("day", r))

# ---- the hourly ingest job end to end ----
c = reset()
out = ingest.handler({}, None)
keys = sorted(c.items)
expect("ingest stores fires#latest", "fires#latest" in keys)
expect("ingest precomputes 5 smoke results and 5 air-quality series",
       sum(k.startswith("smoke#") for k in keys) >= 4 and sum(k.startswith("aq#") for k in keys) >= 4 and out["smoke_results"] == 5 and out["air_series"] == 5, (out, keys))
expect("ingest reports no errors on a healthy run", out["errors"] == [], out["errors"])
f0, w0 = calls["firms"], calls["wind"]
r = smoke.handler({"queryStringParameters": {"lat": "28.61", "lon": "77.21"}}, None)
b = json.loads(r["body"])
expect("after ingest, /smoke answers from cache with no upstream calls", r["statusCode"] == 200 and b["data_quality"]["served_from"] == "cache" and calls["firms"] == f0 and calls["wind"] == w0)
expect("/smoke body valid", not check_response("smoke", b))
f1, w1 = calls["firms"], calls["wind"]
ingest.handler({}, None)
expect("second hourly run recomputes results (5 new wind calls) but fetches FIRMS only once", calls["wind"] - w1 == 5 and calls["firms"] - f1 == 1, (calls["wind"] - w1, calls["firms"] - f1))
c = reset(); state["firms_down"] = True
try:
    ingest.handler({}, None); expect("ingest raises when FIRMS is down and nothing is cached", False)
except firms.FirmsError:
    expect("ingest raises when FIRMS is down and nothing is cached (the run is visibly failed)", True)
c = reset()
orig = weather.fetch_wind
def flaky(lat, lon, now_ist_naive, hours=48, timeout=8):
    if abs(lat - 13.08) < 0.01: raise weather.WeatherError("down")
    return orig(lat, lon, now_ist_naive, hours, timeout)
weather.fetch_wind = flaky
out = ingest.handler({}, None)
expect("one failing city does not stop the others", out["smoke_results"] == 4 and len(out["errors"]) == 1 and "chennai" in out["errors"][0], out)
weather.fetch_wind = orig

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
