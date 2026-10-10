"""Shared tooling for replays and validation. Pure functions (tested offline) + network fetchers (run by you).
The fetchers use FIRMS standard-processing archives and Open-Meteo archives. Results are cached in scripts/.cache/."""
import json
import os
import sys
from datetime import datetime, timedelta, timezone, date

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "backend"))
from lib import firms, weather, smoke_logic, day_logic   # noqa: E402

IST = smoke_logic.IST
SP_SOURCES = ["VIIRS_SNPP_SP", "VIIRS_NOAA20_SP", "VIIRS_NOAA21_SP"]
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
CACHE = os.path.join(ROOT, "scripts", ".cache")
LATENCY_H = 3   # real-time fire data arrives about 3 h after the satellite pass; replays hide anything newer


# ---------------- config ----------------
def load_config():
    with open(os.path.join(ROOT, "scripts", "events.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    with open(os.path.join(ROOT, "backend", "config", "cities.json"), encoding="utf-8") as f:
        cities = {c["id"]: c for c in json.load(f)["cities"]}
    return cfg, cities


# ---------------- pure logic (offline-tested) ----------------
def find_jump(times, pm25, lo, hi, threshold=90.0, surge=1.5):
    """Find the hour of the spike in a CAMS PM2.5 series (times are 'YYYY-MM-DDTHH:MM', IST).
    Rule A: first hour at or above `threshold` after a day entirely below it. Rule B (if the air was already
    poor): first hour at or above 60 that is `surge` times the previous 24 h mean. Returns (time, rule) or (None, None)."""
    idx = [i for i, t in enumerate(times) if lo <= t <= hi and pm25[i] is not None]

    def prev(i, n=24):
        return [v for v in pm25[max(0, i - n):i] if v is not None]

    for i in idx:
        p = prev(i)
        if pm25[i] >= threshold and p and max(p) < threshold:
            return times[i], "crossing"
    for i in idx:
        p = prev(i)
        if p and pm25[i] >= 60 and pm25[i] >= surge * (sum(p) / len(p)):
            return times[i], "surge"
    return None, None


def _prep(city, fires, wind_data, as_of_ist):
    as_of_utc = as_of_ist.astimezone(timezone.utc)
    visible = [f for f in fires if f["t"] <= as_of_utc - timedelta(hours=LATENCY_H)]
    cells = firms.cluster(visible, as_of_utc)
    newest = max((f["t"] for f in visible), default=None)
    age = 0 if newest is None else max(0.0, (as_of_utc - newest).total_seconds() / 3600)
    wind = weather.parse_wind(wind_data, as_of_ist.replace(tzinfo=None), hours=24)
    return as_of_utc, cells, age, wind


def simulate(city, fires, wind_data, as_of_ist, festival=None):
    """Run the normal smoke logic as it would have run at `as_of_ist`. No look-ahead on fires: detections newer
    than as_of minus LATENCY_H are hidden. (Wind is archived reanalysis, i.e. a perfect 'forecast': say so.)"""
    as_of_utc, cells, age, wind = _prep(city, fires, wind_data, as_of_ist)
    return smoke_logic.build_smoke(city["lat"], city["lon"], city["label"], cells, wind, as_of_utc, age,
                                   festival=festival, served_from="replay")


def simulate_score(city, fires, wind_data, as_of_ist):
    """(raw risk score, number of fire detections counted) for threshold tuning."""
    _, cells, _, wind = _prep(city, fires, wind_data, as_of_ist)
    w = smoke_logic.summarize_wind(smoke_logic.effective_wind(wind))
    kept = smoke_logic.select_cells(city["lat"], city["lon"], cells, w["from_deg"], w["net_speed"])
    return sum(k["score"] for k in kept), sum(k["cell"]["n24"] for k in kept)


def sweep(thresholds, calm_scores, event_scores):
    """For each candidate 'medium' threshold: false alarms on calm mornings, and which events would still be warned
    (some as-of at least 12 h before the spike scores at or above it). event_scores: {id: {hours_before: score}}."""
    out = []
    for t in thresholds:
        alarms = sum(1 for sc in calm_scores if sc >= t)
        hits = {i: max([v for h, v in d.items() if h >= 12] or [0]) >= t for i, d in event_scores.items()}
        out.append({"t": t, "alarms": alarms, "hits": hits})
    return out


def make_replay_files(event, city, fires, wind_data, cams_data, as_of_ist):
    """Contract-shaped smoke.json and day.json for one event."""
    smoke = simulate(city, fires, wind_data, as_of_ist)
    smoke["mode"] = "replay"
    smoke["replay"] = {"event_id": event["id"], "label_key": event["label_key"],
                       "as_of": as_of_ist.isoformat(timespec="seconds")}
    smoke["generated_at"] = as_of_ist.isoformat(timespec="seconds")
    hourly = weather.parse_air_quality(cams_data, as_of_ist.date())
    day = day_logic.build_day(hourly, "general", as_of_ist.date().isoformat(),
                              {"lat": city["lat"], "lon": city["lon"], "label": city["label"]}, served_from="replay")
    return smoke, day


def evaluate(rows):
    """rows: [{'h': hours_before_spike, 'risk': ...}]. Hit = medium or high at least 12 h before the spike.
    Returns (hit, lead_hours): lead = the earliest such warning."""
    warned = [r["h"] for r in rows if r["h"] >= 12 and r["risk"] in ("medium", "high")]
    return (True, max(warned)) if warned else (False, None)


# ---------------- network fetchers (not tested offline) ----------------
def _cached(name, fn):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name + ".json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    data = fn()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return data


def fetch_fires_archive(key, start, end, sources=SP_SOURCES):
    """Fire detections for [start, end] (datetime.date), India box, from the SP archives. Returns (fires, notes)."""
    fires, notes, got = [], [], 0
    d = start
    while d <= end:
        n = min(5, (end - d).days + 1)
        for s in sources:
            try:
                rows = firms.parse_csv(firms.fetch_csv(key, s, days=n, date=d.isoformat(), timeout=60))
                fires.extend(rows); got += 1
            except firms.FirmsError as e:
                notes.append(f"{s} {d}: {str(e).replace(key, '***')[:70]}")
        d += timedelta(days=n)
    if got == 0:
        raise firms.FirmsError("no FIRMS archive source answered: " + "; ".join(notes[:3]))
    return fires, notes


def fetch_wind_archive(lat, lon, start, end):
    base = {"latitude": lat, "longitude": lon, "start_date": start.isoformat(), "end_date": end.isoformat(),
            "timezone": "Asia/Kolkata"}
    import urllib.parse
    for hourly in ("wind_speed_10m,wind_direction_10m,wind_speed_850hPa,wind_direction_850hPa",
                   "wind_speed_10m,wind_direction_10m"):
        try:
            return weather.fetch_json(ARCHIVE_URL + "?" + urllib.parse.urlencode({**base, "hourly": hourly}), timeout=60)
        except weather.WeatherError:
            continue
    raise weather.WeatherError("Open-Meteo wind archive unavailable")


def fetch_cams(lat, lon, start, end):
    import urllib.parse
    q = {"latitude": lat, "longitude": lon, "hourly": "pm2_5,pm10", "start_date": start.isoformat(),
         "end_date": end.isoformat(), "timezone": "Asia/Kolkata"}
    return weather.fetch_json(AQ_URL + "?" + urllib.parse.urlencode(q), timeout=60)


def event_data(event, city, key):
    """Everything needed for one event, cached on disk. Fire data is fetched from 3 days before the window."""
    s, e = (date.fromisoformat(x) for x in event["window"])
    fs, fe = s - timedelta(days=3), e + timedelta(days=1)

    def fires_rows():
        fires, notes = fetch_fires_archive(key, fs, fe)
        return {"notes": notes, "rows": [[f["lat"], f["lon"], f["frp"], f["t"].isoformat()] for f in fires]}

    packed = _cached(f"fires-{event['id']}", fires_rows)
    fires = [{"lat": r[0], "lon": r[1], "frp": r[2], "t": datetime.fromisoformat(r[3])} for r in packed["rows"]]
    wind = _cached(f"wind-{event['id']}", lambda: fetch_wind_archive(city["lat"], city["lon"], fs, fe))
    cams = _cached(f"cams-{event['id']}", lambda: fetch_cams(city["lat"], city["lon"], fs, fe))
    return {"fires": fires, "wind": wind, "cams": cams, "notes": packed["notes"]}


def daily_summary(cams_data, start, end):
    """[(date_str, mean_pm25, max_pm25)] from the CAMS series, to eyeball where the real jump is."""
    h, out = cams_data["hourly"], []
    for d in sorted({t[:10] for t in h["time"]}):
        if start <= d <= end:
            v = [x for t, x in zip(h["time"], h["pm2_5"]) if t.startswith(d) and x is not None]
            if v:
                out.append((d, round(sum(v) / len(v)), round(max(v))))
    return out


def spike_time(event, cams_data, mode="cams"):
    """(aware IST datetime, how_found). mode='cpcb' uses the CPCB-reported spike day from events.json.
    mode='cams' finds it in the CAMS series and falls back to the CPCB day if there is no clear jump."""
    if mode == "cpcb" and event.get("cpcb_target"):
        return datetime.fromisoformat(event["cpcb_target"]).replace(tzinfo=IST), "CPCB date"
    h = cams_data["hourly"]
    lo, hi = event["window"][0] + "T00:00", event["window"][1] + "T23:00"
    t, rule = find_jump(h["time"], h["pm2_5"], lo, hi)
    if t:
        return datetime.fromisoformat(t).replace(tzinfo=IST), f"CAMS {rule}"
    return datetime.fromisoformat(event["cpcb_target"]).replace(tzinfo=IST), "CPCB date (no clear CAMS jump)"
