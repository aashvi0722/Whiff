"""Smoke-arrival heuristic (playbook 5.1 / 5.2). Pure functions: no network, easy to test.
This is a transparent heuristic, NOT a dispersion model. All thresholds are tunable placeholders."""
import math
from datetime import timedelta, timezone

from .geo import (haversine_km, bearing_deg, angle_diff, circular_mean, circular_spread_deg)

IST = timezone(timedelta(hours=5, minutes=30))
RADIUS_KM = 700
MAX_TRAVEL_H = 48
MIN_ALIGN = 0.5
SPEED_FLOOR = 5.0          # km/h; calm wind => "too slow"
FIRE_STALE_H = 15          # VIIRS passes roughly every 12 h (about 01:30 and 13:30 local) plus a few hours of latency,
                           # so the playbook's 6 h was too strict: it would mark half of every day "stale".
# none < 40 <= low < 75 <= medium < 200 <= high.  Calibrated with scripts/tune.py on 3 past events + one calm week;
# the two backup events were held out and still warned. Original guesses were (5, 30, 120): they raised 6 false
# alarms in 8 calm mornings. 'high' (200) rests on very few events: treat it as the least reliable number.
RISK_THRESHOLDS = (40, 75, 200)
CROP_REGIONS = ("IN-PB", "IN-HR", "IN-UP")
LEVELS = ["low", "medium", "high"]


def _motion(speed, dir_from):
    """East/north components of where the air is moving TO."""
    to = math.radians((dir_from + 180) % 360)
    return speed * math.sin(to), speed * math.cos(to)


def effective_wind(samples):
    """Blend 10 m and 850 hPa winds (when present) into one (speed, dir_from) per hour."""
    out = []
    for s in samples:
        vs = [_motion(s[sk], s[dk]) for sk, dk in (("s10", "d10"), ("s850", "d850"))
              if s.get(sk) is not None and s.get(dk) is not None]
        if not vs:
            continue
        e = sum(v[0] for v in vs) / len(vs)
        n = sum(v[1] for v in vs) / len(vs)
        to = (math.degrees(math.atan2(e, n)) + 360) % 360
        out.append((math.hypot(e, n), (to + 180) % 360))
    return out


def summarize_wind(eff):
    """Net wind over the window. net_speed = vector mean (variable wind => slow net transport)."""
    es = [_motion(s, d) for s, d in eff]
    e = sum(v[0] for v in es) / len(es)
    n = sum(v[1] for v in es) / len(es)
    net_speed = math.hypot(e, n)
    from_deg = (math.degrees(math.atan2(e, n)) + 180) % 360
    _, r = circular_mean([d for _, d in eff], [max(s, 0.1) for s, _ in eff])
    return {"from_deg": from_deg, "net_speed": net_speed,
            "mean_speed": sum(s for s, _ in eff) / len(eff), "spread": circular_spread_deg(r)}


def select_cells(user_lat, user_lon, cells, from_deg, net_speed):
    travel_dir = (from_deg + 180) % 360
    kept = []
    for c in cells:
        if c["n24"] <= 0:
            continue
        d = haversine_km(c["lat"], c["lon"], user_lat, user_lon)
        if d > RADIUS_KM:
            continue
        b_cell_to_user = bearing_deg(c["lat"], c["lon"], user_lat, user_lon)
        align = 1.0 if d < 5 else math.cos(math.radians(angle_diff(travel_dir, b_cell_to_user)))
        if align < MIN_ALIGN:
            continue
        travel = d / max(net_speed * align, SPEED_FLOOR)
        if travel > MAX_TRAVEL_H:
            continue
        kept.append({"cell": c, "d": d, "align": align, "travel": travel,
                     "score": c["n24"] * max(0.0, 1 - d / RADIUS_KM) * align,
                     "brg_user_to_cell": (b_cell_to_user + 180) % 360})
    return kept


def risk_level(score):
    lo, mid, hi = RISK_THRESHOLDS
    return "none" if score < lo else "low" if score < mid else "medium" if score < hi else "high"


def weighted_percentile(pairs, q):
    pairs = sorted(pairs, key=lambda p: p[0])
    total = sum(w for _, w in pairs)
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= q * total - 1e-12:
            return v
    return pairs[-1][0]


def fire_trend(kept):
    n24 = sum(k["cell"]["n24"] for k in kept)
    nprev = sum(k["cell"]["nprev"] for k in kept)
    if n24 == 0:
        return "none"
    if nprev == 0:
        return "rising"
    ratio = n24 / nprev
    return "rising" if ratio > 1.2 else "steady" if ratio >= 0.8 else "falling"


def confidence(risk, spread, trend, arrival, age):
    """Playbook 5.2. Returns (level, reasons). 'region_cloudy' is not computed (no cloud data)."""
    reasons = []
    if spread < 30:
        reasons.append("wind_steady")
    elif spread > 45:
        reasons.append("wind_variable")
    if risk != "none" and trend in ("rising", "steady"):
        reasons.append("fires_rising" if trend == "rising" else "fires_steady")
    if arrival is not None:
        if arrival < 24:
            reasons.append("arrival_soon")
        elif arrival > 36:
            reasons.append("arrival_far")
    if age > FIRE_STALE_H:
        reasons.append("fires_stale")
    if risk == "none":
        level = 0 if age > FIRE_STALE_H else (1 if spread > 30 else 2)
    else:
        level = 1
        if spread < 30 and trend in ("rising", "steady") and arrival < 24:
            level += 1
        if spread > 45 or arrival > 36 or age > FIRE_STALE_H:
            level -= 1
    return LEVELS[max(0, min(2, level))], reasons


def build_smoke(lat, lon, label, cells, wind_samples, now, fires_age_hours,
                festival=None, stale=False, served_from="live"):
    """Return a /smoke response in the contract shape. `now` must be timezone-aware."""
    festival = festival or {"active": False, "name": None}
    eff = effective_wind(wind_samples[:24])
    if not eff:
        raise ValueError("no usable wind data")
    w = summarize_wind(eff)
    kept = select_cells(lat, lon, cells, w["from_deg"], w["net_speed"])
    score = sum(k["score"] for k in kept)
    risk = risk_level(score)
    now_ist = now.astimezone(IST)
    age = fires_age_hours if fires_age_hours is not None else 0

    arrival = rng = None
    sources, reasons = [], []
    if risk != "none":
        pairs = [(k["travel"], k["score"]) for k in kept]
        arrival = max(1, round(weighted_percentile(pairs, 0.5)))
        rng = [max(1, round(weighted_percentile(pairs, 0.25))), max(1, round(weighted_percentile(pairs, 0.75)))]
        groups = {}
        for k in kept:
            groups.setdefault(k["cell"]["region"], []).append(k)
        for region, ks in groups.items():
            ws = [k["score"] for k in ks]
            bearing, _ = circular_mean([k["brg_user_to_cell"] for k in ks], ws)
            crop = region in CROP_REGIONS and now_ist.month in (10, 11)
            sources.append({
                "type": "crop_residue_likely" if crop else "unknown",
                "region_code": region,
                "fire_count": sum(k["cell"]["n24"] for k in ks),
                "distance_km": round(sum(k["d"] * k["score"] for k in ks) / sum(ws)),
                "bearing_deg": round(bearing) % 360,
                "travel_hours": max(1, round(weighted_percentile([(k["travel"], k["score"]) for k in ks], 0.5)))})
        sources = sorted(sources, key=lambda s: -s["fire_count"])[:3]
        km = round(sum(k["d"] * k["score"] for k in kept) / score)
        reasons.append({"code": "smoke_aligned_fires",
                        "params": {"count": sum(k["cell"]["n24"] for k in kept), "km": km}})
    else:
        reasons.append({"code": "smoke_none_upwind", "params": {}})
        if not kept:
            reasons.append({"code": "wind_from_clean_sector", "params": {}})

    if w["mean_speed"] < 8:
        reasons.append({"code": "wind_calm_trapping", "params": {}})
    if festival.get("active"):
        reasons.append({"code": "festival_night", "params": {"name": festival.get("name")}})
    if stale:
        reasons.append({"code": "data_stale", "params": {}})

    conf, conf_reasons = confidence(risk, w["spread"], fire_trend(kept), arrival, age)
    return {
        "contract_version": 1, "mode": "live", "replay": None,
        "location": {"lat": lat, "lon": lon, "label": label},
        "generated_at": now_ist.isoformat(timespec="seconds"),
        "risk": risk, "arrival_hours": arrival, "arrival_range_hours": rng,
        "confidence": conf, "confidence_reasons": conf_reasons, "sources": sources,
        "wind": {"from_deg": round(w["from_deg"]) % 360, "speed_kmh": round(w["mean_speed"]),
                 "steady": w["spread"] < 30},
        "festival": {"active": bool(festival.get("active")), "name": festival.get("name")},
        "reason_codes": reasons,
        "data_quality": {"fires_age_hours": round(age), "stale": bool(stale), "served_from": served_from},
    }
