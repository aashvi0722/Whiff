#!/usr/bin/env python3
"""Run the stub handlers locally with fake API Gateway events (no AWS needed).
From the repo root:  python scripts/test_stub_local.py"""
import json, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "backend"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import smoke, day, history, replays          # noqa: E402
from check_contract import check_response    # noqa: E402

fails = 0

def call(mod, q=None):
    r = mod.handler({"queryStringParameters": q}, None)
    return r["statusCode"], json.loads(r["body"])

def expect(label, ok, extra=""):
    global fails
    print(("ok   " if ok else "FAIL ") + label + (f"  {extra}" if extra and not ok else ""))
    fails += 0 if ok else 1

s, b = call(smoke, {"scenario": "smoke_high"})
expect("smoke scenario=smoke_high, valid", s == 200 and b["risk"] == "high" and not check_response("smoke", b))
s, b = call(smoke, {"scenario": "smoke_none"})
expect("smoke scenario=smoke_none", s == 200 and b["risk"] == "none" and not check_response("smoke", b))
s, b = call(smoke, {"scenario": "smoke_stale"})
expect("smoke scenario=smoke_stale", s == 200 and b["data_quality"]["stale"] is True)
s, b = call(smoke, {"scenario": "error"})
expect("smoke scenario=error -> 503", s == 503 and b["error"]["code"] == "upstream_unavailable")
s, b = call(smoke, {"replay": "delhi-nov-2025"})
expect("smoke replay=delhi-nov-2025", s == 200 and b["mode"] == "replay" and not check_response("smoke", b))
s, b = call(smoke, {"replay": "bogus"})
expect("smoke replay=bogus -> 404", s == 404 and b["error"]["code"] == "unknown_replay")
s, b = call(smoke, {"scenario": "no_such_thing"})
expect("smoke unknown scenario falls back", s == 200 and b["risk"] == "high")
s, b = call(smoke, {"scenario": "day_windows"})
expect("smoke ignores another endpoint's scenario", s == 200 and "risk" in b)
# --- real /smoke input handling and failure shapes (network replaced by fakes) ---
for q, label in [(None, "no query"), ({"lat": "0", "lon": "0"}, "lat=0 lon=0"), ({"lat": "abc", "lon": "77"}, "non-numeric"),
                 ({"lat": "nan", "lon": "77"}, "nan"), ({"lat": "28.6"}, "missing lon"), ({"lat": "60", "lon": "77"}, "out of India")]:
    s, b = call(smoke, q)
    expect(f"smoke bad input rejected politely ({label})", s == 400 and b["error"]["code"] == "invalid_location" and not check_response("error", b))
import json as _json
_real = smoke.compute_live
smoke.compute_live = lambda lat, lon, now: _json.load(open(os.path.join(ROOT, "contract", "smoke_none.sample.json")))
s, b = call(smoke, {"lat": "12.97", "lon": "77.59"})
expect("smoke live path returns 200 contract body", s == 200 and b["risk"] == "none")
def _boom(*a, **k): raise RuntimeError("secret-key-123 exploded")
smoke.compute_live = _boom
s, b = call(smoke, {"lat": "28.6", "lon": "77.2"})
expect("smoke upstream failure => 503 error shape, no trace", s == 503 and b["error"]["code"] == "upstream_unavailable" and "secret" not in json.dumps(b))
smoke.compute_live = _real
s, b = call(day, {"audience": "child"})
expect("day default = windows, valid", s == 200 and b["day_state"] == "windows" and not check_response("day", b))
for sc, st in [("day_caution", "caution"), ("day_stay_in", "stay_in")]:
    s, b = call(day, {"scenario": sc})
    expect(f"day scenario={sc}", s == 200 and b["day_state"] == st and not check_response("day", b))
s, b = call(history)
expect("history", s == 200 and not check_response("history", b))
s, b = call(replays)
expect("replays", s == 200 and not check_response("replays", b))
print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
