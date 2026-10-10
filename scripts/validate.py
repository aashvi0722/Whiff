#!/usr/bin/env python3
"""Validation run (add --target cpcb to grade against the CPCB spike day instead of the CAMS-detected hour): for each smoke event, run the smoke logic as of 48/36/24/12 h before the spike; for the calm
period, run it every morning. Prints a markdown table.   python scripts/validate.py [--write] [--backups]
--write puts the table into docs/architecture.md (section 5)."""
import os, sys
from datetime import timedelta, date
import replay_tools as rt

key = os.environ.get("FIRMS_KEY", "")
if not key:
    sys.exit("FIRMS_KEY is not set in this terminal.")
target = sys.argv[sys.argv.index("--target") + 1] if "--target" in sys.argv else "cams"
cfg, cities = rt.load_config()
events = cfg["events"] + (cfg["backups"] if "--backups" in sys.argv else [])
lines = ["| Event | As-of | Predicted risk | Predicted arrival | Confidence | Actual jump (how found) | Lead if warned | Hit? |",
         "|---|---|---|---|---|---|---|---|"]
summary = []
for ev in events:
    city = cities[ev["city"]]
    d = rt.event_data(ev, city, key)
    if ev["kind"] == "calm":
        s, e = (date.fromisoformat(x) for x in ev["window"])
        alarms, days = 0, 0
        cur = s
        while cur <= e:
            as_of = rt.datetime.combine(cur, rt.datetime.min.time()).replace(hour=6, tzinfo=rt.IST)
            r = rt.simulate(city, d["fires"], d["wind"], as_of)
            bad = r["risk"] in ("medium", "high"); alarms += bad; days += 1
            lines.append(f"| {ev['id']} | {as_of:%b %d 06:00} | {r['risk']} | {r['arrival_hours'] or '-'} | {r['confidence']} | no spike (calm) | - | {'FALSE ALARM' if bad else 'correct'} |")
            cur += timedelta(days=1)
        summary.append(f"{ev['id']}: {alarms} false alarm(s) in {days} calm mornings")
        continue
    spike, how = rt.spike_time(ev, d["cams"], target)
    rows = []
    for h in (48, 36, 24, 12):
        as_of = spike - timedelta(hours=h)
        r = rt.simulate(city, d["fires"], d["wind"], as_of)
        rows.append({"h": h, "risk": r["risk"]})
        arr = f"{r['arrival_hours']} h" if r["arrival_hours"] else "-"
        lines.append(f"| {ev['id']} | {h} h before ({as_of:%b %d %H:%M}) | {r['risk']} | {arr} | {r['confidence']} | {spike:%b %d %H:%M} ({how}) | | |")
    hit, lead = rt.evaluate(rows)
    lines.append(f"| **{ev['id']}** | **verdict** | | | | | {str(lead) + ' h' if lead else '-'} | **{'HIT' if hit else 'MISS'}** |")
    summary.append(f"{ev['id']}: {'HIT, warned ' + str(lead) + ' h ahead' if hit else 'MISS (no medium/high warning 12+ h ahead)'}")
table = "\n".join(lines)
print(table)
print("\nSummary:")
for s in summary:
    print(" -", s)
print("\nCaveats: archived wind is reanalysis (a perfect forecast), CAMS is a ~45 km model with 3-hourly steps, tiny sample.")
if "--write" in sys.argv:
    path = os.path.join(rt.ROOT, "docs", "architecture.md")
    text = open(path, encoding="utf-8").read()
    a, b = "<!-- validation:start -->", "<!-- validation:end -->"
    if a not in text:
        text = text.replace("TODO (S4)", a + "\n" + b, 1)
    if a in text and b in text:
        block = table + "\n\n" + "\n".join("- " + s for s in summary) + "\n\nCaveats: archived wind is reanalysis, not a forecast (replays are slightly easier than real life); CAMS is a ~45 km model with 3-hourly steps; very small sample."
        text = text[:text.index(a) + len(a)] + "\n" + block + "\n" + text[text.index(b):]
        open(path, "w", encoding="utf-8").write(text)
        print("\nwritten to docs/architecture.md")
    else:
        print("\ncould not find the validation section in docs/architecture.md; paste the table by hand")
