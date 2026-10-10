#!/usr/bin/env python3
"""Threshold tuning. Prints the raw smoke score for every event as-of time and calm morning, then sweeps candidate
'medium' thresholds. Tuning set = main events + calm week. HOLD-OUT = the backup events (never used to choose).
    python scripts/tune.py            (uses the cached downloads from make_replay.py / validate.py)"""
import os, sys
from datetime import timedelta, date
import replay_tools as rt

key = os.environ.get("FIRMS_KEY", "")
if not key:
    sys.exit("FIRMS_KEY is not set in this terminal.")
cfg, cities = rt.load_config()
tune_ev = {}; hold_ev = {}; calm = []
print("Raw risk scores (higher = more fire weight upwind). Live thresholds today: low>=5, medium>=30, high>=120\n")
for group, evs in (("TUNING", cfg["events"]), ("HOLD-OUT", cfg["backups"])):
    for ev in evs:
        city = cities[ev["city"]]
        d = rt.event_data(ev, city, key)
        if ev["kind"] == "calm":
            s, e = (date.fromisoformat(x) for x in ev["window"])
            cur = s
            while cur <= e:
                as_of = rt.datetime.combine(cur, rt.datetime.min.time()).replace(hour=6, tzinfo=rt.IST)
                sc, n = rt.simulate_score(city, d["fires"], d["wind"], as_of)
                calm.append(sc); print(f"{group:8} {ev['id']:22} {cur:%b %d 06:00}          score {sc:7.1f}  fires counted {n}")
                cur += timedelta(days=1)
            continue
        spike, how = rt.spike_time(ev, d["cams"], "cpcb")
        row = {}
        for h in (48, 36, 24, 12):
            sc, n = rt.simulate_score(city, d["fires"], d["wind"], spike - timedelta(hours=h))
            row[h] = sc; print(f"{group:8} {ev['id']:22} {h:2d} h before          score {sc:7.1f}  fires counted {n}")
        (tune_ev if group == "TUNING" else hold_ev)[ev["id"]] = row
cands = [5, 10, 20, 30, 50, 75, 100, 150, 200, 300, 500]
print(f"\nCalm mornings: {len(calm)}; highest calm score {max(calm):.1f}")
print("\nThreshold sweep for 'medium' (warn if score >= threshold):")
print("threshold | calm false alarms | tuning events warned >=12 h ahead | hold-out events warned")
for r_t, r_h in zip(rt.sweep(cands, calm, tune_ev), rt.sweep(cands, calm, hold_ev)):
    th = sum(r_t["hits"].values()); hh = sum(r_h["hits"].values())
    print(f"{r_t['t']:9} | {r_t['alarms']:2d} of {len(calm)}           | {th} of {len(tune_ev)}                              | {hh} of {len(hold_ev)}")
print("\nCaveat: the calm week is one week and the events are few, so this is calibration, not proof of accuracy.")
