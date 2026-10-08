"""Plan-my-day logic: hourly status, clean-air windows, day state (playbook 5.4). Pure functions."""
from .bands import AUDIENCES, aqi_from, band_of, status_for

FIRST_H, LAST_H, LAST_ACTIVE_H = 5, 22, 21


def build_day(hourly, audience, date_iso, location, wake_h=None, served_from="live"):
    """hourly: {hour: (pm25, pm10_or_None)}. Gaps and None values are skipped, never crash."""
    if audience not in AUDIENCES:
        audience = "general"
    start = FIRST_H
    if wake_h is not None:
        start = min(max(int(wake_h), FIRST_H), 12)

    rows = []
    for h in sorted(hourly):
        pm25, pm10 = hourly[h]
        if pm25 is None or h < FIRST_H or h > LAST_H:
            continue
        a = aqi_from(pm25, pm10)
        rows.append({"h": h, "pm25": round(pm25), "aqi": a, "band": band_of(a),
                     "status": status_for(a, audience), "_raw": pm25})
    if not rows:
        raise ValueError("no hourly air-quality data for the day")
    missing = (LAST_H - FIRST_H + 1) - len(rows)
    active = [r for r in rows if start <= r["h"] <= LAST_ACTIVE_H]
    if not active:
        raise ValueError("no hours inside the active window")

    # windows = unbroken runs of go hours (a missing hour breaks a run)
    runs, cur = [], []
    for r in active:
        if r["status"] == "go" and (not cur or r["h"] == cur[-1]["h"] + 1):
            cur.append(r)
        else:
            if cur:
                runs.append(cur)
            cur = [r] if r["status"] == "go" else []
    if cur:
        runs.append(cur)

    day_avg = sum(r["_raw"] for r in active) / len(active)
    wins = []
    for run in runs:
        avg = sum(r["_raw"] for r in run) / len(run)
        mean_aqi = round(sum(r["aqi"] for r in run) / len(run))
        wins.append({"start_h": run[0]["h"], "end_h": run[-1]["h"], "avg_pm25": round(avg),
                     "band": band_of(mean_aqi), "_avg": round(avg, 1), "_len": len(run), "_pct": (day_avg - avg) / day_avg * 100})
    wins.sort(key=lambda w: (w["_avg"], -w["_len"]))
    wins = wins[:3]
    for i, w in enumerate(wins, 1):
        pct = round(w["_pct"])
        code = {"code": "pm25_below_avg", "params": {"percent": pct}} if pct >= 0 else \
               {"code": "pm25_above_avg", "params": {"percent": abs(pct)}}
        w["rank"], w["reason_codes"] = i, [code]
        for k in ("_avg", "_len", "_pct"):
            del w[k]

    best = min(active, key=lambda r: r["_raw"])["h"]
    worst = max(active, key=lambda r: r["_raw"])["h"]
    max_aqi = max(r["aqi"] for r in active)
    if wins:
        state = "windows"
        reasons = [{"code": "best_hour", "params": {"hour": best}}, {"code": "worst_hour", "params": {"hour": worst}}]
    elif all(r["status"] == "stay" for r in active):
        state = "stay_in"
        reasons = [{"code": "all_day_poor", "params": {"hour": best}}]
    else:
        state = "caution"
        reasons = [{"code": "best_hour", "params": {"hour": best}}]

    advice = []
    if any(r["status"] != "go" for r in active if 17 <= r["h"] <= LAST_ACTIVE_H):
        advice.append("keep_windows_closed_evening")
    if state == "stay_in":
        advice += ["indoor_swap", "run_purifier"]
    if state in ("caution", "stay_in"):
        advice += ["mask_n95_outdoors", "delay_outdoor_events"]
    if audience == "outdoor" and (state != "windows" or max_aqi > 200):
        advice.append("shift_heavy_work")
    advice = list(dict.fromkeys(advice))

    nongo = sum(1 for r in active if r["status"] != "go")
    hours = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]
    return {
        "contract_version": 1, "date": date_iso, "audience": audience, "location": location,
        "day_state": state, "aqi_is_estimate": True, "hours": hours, "windows": wins,
        "best_hour": best, "worst_hour": worst, "day_avg_pm25": round(day_avg),
        "exposure_avoided_hours": nongo,
        "cigarette_equiv": {"value": round(day_avg / 22), "approx": True},
        "reason_codes": reasons, "advice_codes": advice,
        "data_quality": {"stale": False, "served_from": served_from, "missing_hours": missing},
    }
