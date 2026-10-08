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

s, b = call(smoke, {"lat": "28.6", "lon": "77.2"})
expect("smoke default = high, valid", s == 200 and b["risk"] == "high" and not check_response("smoke", b))
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
s, b = call(smoke, None)
expect("smoke with no query string", s == 200)
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
