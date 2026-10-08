"""Open-Meteo wind forecast (10 m plus 850 hPa). Standard library only.
Credit Open-Meteo.com (CC BY 4.0, free tier is non-commercial)."""
import json
import urllib.parse
import urllib.request
from datetime import datetime

FORECAST = "https://api.open-meteo.com/v1/forecast"
HOURLY = "wind_speed_10m,wind_direction_10m,wind_speed_850hPa,wind_direction_850hPa"


class WeatherError(Exception):
    pass


def wind_url(lat, lon, days=3):
    q = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "hourly": HOURLY,
                                "forecast_days": days, "timezone": "Asia/Kolkata"})
    return f"{FORECAST}?{q}"


def fetch_json(url, timeout=8):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        raise WeatherError(f"{type(e).__name__}: {e}") from None


def parse_wind(data, now_ist_naive, hours=48):
    """Return the next `hours` samples starting at the current hour:
    [{'t','s10','d10','s850','d850'}] (values may be None). Speeds are km/h."""
    try:
        h = data["hourly"]
        times = h["time"]
    except (KeyError, TypeError):
        raise WeatherError("unexpected Open-Meteo response") from None
    cur = now_ist_naive.replace(minute=0, second=0, microsecond=0)

    def col(name):
        return h.get(name) or [None] * len(times)

    s10, d10, s850, d850 = col("wind_speed_10m"), col("wind_direction_10m"), col("wind_speed_850hPa"), col("wind_direction_850hPa")
    out = []
    for i, t in enumerate(times):
        try:
            if datetime.strptime(t, "%Y-%m-%dT%H:%M") < cur:
                continue
        except ValueError:
            continue
        out.append({"t": t, "s10": s10[i], "d10": d10[i], "s850": s850[i], "d850": d850[i]})
        if len(out) >= hours:
            break
    if not out:
        raise WeatherError("no forecast hours returned")
    return out


def fetch_wind(lat, lon, now_ist_naive, hours=48, timeout=8):
    return parse_wind(fetch_json(wind_url(lat, lon), timeout), now_ist_naive, hours)


AIR_QUALITY = "https://air-quality-api.open-meteo.com/v1/air-quality"


def air_quality_url(lat, lon, past_days=3, forecast_days=2):
    q = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "hourly": "pm2_5,pm10",
                                "past_days": past_days, "forecast_days": forecast_days,
                                "timezone": "Asia/Kolkata"})
    return f"{AIR_QUALITY}?{q}"


def parse_air_quality(data, day):
    """Return {hour: (pm25, pm10_or_None)} for the given date (datetime.date), local time."""
    try:
        h = data["hourly"]
        times, pm25 = h["time"], h["pm2_5"]
    except (KeyError, TypeError):
        raise WeatherError("unexpected Open-Meteo air-quality response") from None
    pm10 = h.get("pm10") or [None] * len(times)
    prefix = day.isoformat()
    out = {}
    for i, t in enumerate(times):
        if t.startswith(prefix):
            out[int(t[11:13])] = (pm25[i], pm10[i])
    if not out:
        raise WeatherError("no air-quality hours for today")
    return out
