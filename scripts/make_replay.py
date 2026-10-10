#!/usr/bin/env python3
"""Create replay files for the events in scripts/events.json.
    $env:FIRMS_KEY = "..."           (this terminal only)
    python scripts/make_replay.py                    # all smoke events
    python scripts/make_replay.py delhi-2024-11      # one event
    python scripts/make_replay.py --hours-before 24  # snapshot time before the spike (default 24)
    python scripts/make_replay.py --target cpcb      # use the CPCB spike day instead of the CAMS-detected hour
Writes backend/replays/<event_id>/smoke.json and day.json. Needs network. First run is slow (archives are cached)."""
import json, os, sys
from datetime import timedelta
import replay_tools as rt

key = os.environ.get("FIRMS_KEY", "")
if not key:
    sys.exit("FIRMS_KEY is not set in this terminal.")
args = sys.argv[1:]
hours_before = 24
if "--hours-before" in args:
    i = args.index("--hours-before"); hours_before = int(args[i + 1]); del args[i:i + 2]
target = "cams"
if "--target" in args:
    i = args.index("--target"); target = args[i + 1]; del args[i:i + 2]
cfg, cities = rt.load_config()
events = [e for e in cfg["events"] + cfg["backups"] if e["kind"] == "smoke" and (not args or e["id"] in args)]
if not events:
    sys.exit("no matching smoke event")
for ev in events:
    city = cities[ev["city"]]
    print(f"\n== {ev['id']} ({city['label']}) ==")
    d = rt.event_data(ev, city, key)
    for n in d["notes"][:5]:
        print("   FIRMS note:", n)
    print(f"   fire rows: {len(d['fires'])}")
    print("   CAMS PM2.5 by day (mean / max ug/m3):", "; ".join(f"{a[5:]}: {m}/{x}" for a, m, x in rt.daily_summary(d["cams"], ev["window"][0], ev["window"][1])))
    print("   wind archive:", "10 m + 850 hPa" if "wind_speed_850hPa" in d["wind"]["hourly"] else "10 m only (live app blends 850 hPa too)")
    spike, how = rt.spike_time(ev, d["cams"], target)
    as_of = spike - timedelta(hours=hours_before)
    print(f"   spike time: {spike:%Y-%m-%d %H:%M} IST ({how}); replay snapshot: {as_of:%Y-%m-%d %H:%M} IST")
    smoke, day = rt.make_replay_files(ev, city, d["fires"], d["wind"], d["cams"], as_of)
    out = os.path.join(rt.ROOT, "backend", "replays", ev["id"]); os.makedirs(out, exist_ok=True)
    for name, obj in (("smoke", smoke), ("day", day)):
        with open(os.path.join(out, name + ".json"), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False); f.write("\n")
    print(f"   risk={smoke['risk']} arrival={smoke['arrival_hours']} h confidence={smoke['confidence']} sources={[s['region_code'] for s in smoke['sources']]}")
    print(f"   day_state={day['day_state']}  wrote backend/replays/{ev['id']}/")
