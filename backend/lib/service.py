"""Orchestration shared by the API handlers and the hourly ingest job: cache-first, stale-on-failure."""
import copy
from datetime import datetime

from . import cache as cache_mod
from . import firms, weather, smoke_logic, festival
from .geo import cell_center

FRESH_S = 70 * 60   # results are refreshed hourly; a little slack for a late run


def grid(lat, lon):
    c = cell_center(lat, lon)
    return f"{c[0]}#{c[1]}"


# ---------------- fires ----------------
def _snapshot(cells, newest):
    return {"newest_t": newest.isoformat() if newest else None,
            "cells": [[c["lat"], c["lon"], c["n24"], c["nprev"], c["frp"], c["region"]] for c in cells]}


def _unsnapshot(snap):
    cells = [{"lat": r[0], "lon": r[1], "n24": r[2], "nprev": r[3], "frp": r[4], "region": r[5]} for r in snap["cells"]]
    newest = datetime.fromisoformat(snap["newest_t"]) if snap.get("newest_t") else None
    return cells, newest


def get_fires(cache, key, now_utc, force_refresh=False):
    """Return (cells, newest_detection_time, served_from, stale). Raises FirmsError if nothing is available."""
    if not force_refresh:
        snap, fresh = cache_mod.read(cache, "fires#latest")
        if snap and fresh:
            cells, newest = _unsnapshot(snap)
            return cells, newest, "cache", False
    try:
        fires, errors = firms.fetch_fires(key, now_utc)
    except firms.FirmsError:
        snap, _ = cache_mod.read(cache, "fires#latest")
        if snap:
            cells, newest = _unsnapshot(snap)
            return cells, newest, "cache", True
        raise
    cells = firms.cluster(fires, now_utc)
    newest = max((f["t"] for f in fires), default=None)
    cache_mod.write(cache, "fires#latest", _snapshot(cells, newest), FRESH_S)
    return cells, newest, "live", False


# ---------------- smoke ----------------
def _localize(result, lat, lon, served_from, stale=False):
    r = copy.deepcopy(result)
    r["location"] = {"lat": lat, "lon": lon, "label": festival.city_label(lat, lon)}
    r["data_quality"]["served_from"] = served_from
    if stale:
        r["data_quality"]["stale"] = True
        if not any(c["code"] == "data_stale" for c in r["reason_codes"]):
            r["reason_codes"].append({"code": "data_stale", "params": {}})
    return r


def compute_smoke(lat, lon, now_utc, cache, key, recompute=False):
    """recompute=True skips the cached RESULT (used by the hourly ingest); fire data still comes cache-first."""
    pk = "smoke#" + grid(lat, lon)
    if not recompute:
        val, fresh = cache_mod.read(cache, pk)
        if val and fresh:
            return _localize(val, lat, lon, "cache")
    try:
        cells, newest, src, fires_stale = get_fires(cache, key, now_utc)
        now_ist = now_utc.astimezone(smoke_logic.IST)
        wind = weather.fetch_wind(lat, lon, now_ist.replace(tzinfo=None))
        age = 0 if newest is None else max(0.0, (now_utc - newest).total_seconds() / 3600)
        res = smoke_logic.build_smoke(
            lat, lon, festival.city_label(lat, lon), cells, wind, now_utc, age,
            festival=festival.festival_for(now_ist.date()), stale=fires_stale, served_from=src)
    except (firms.FirmsError, weather.WeatherError, ValueError):
        val, _ = cache_mod.read(cache, pk)
        if val:
            return _localize(val, lat, lon, "cache", stale=True)
        raise
    cache_mod.write(cache, pk, res, FRESH_S)
    return res


# ---------------- air quality (feeds /day) ----------------
def get_hourly(cache, lat, lon, day, force=False):
    """Return ({hour: (pm25, pm10)}, served_from) where served_from is live | cache | stale."""
    pk = f"aq#{grid(lat, lon)}#{day.isoformat()}"
    if not force:
        val, fresh = cache_mod.read(cache, pk)
        if val and fresh:
            return {int(h): tuple(v) for h, v in val.items()}, "cache"
    try:
        data = weather.fetch_json(weather.air_quality_url(lat, lon, past_days=0, forecast_days=1))
        hourly = weather.parse_air_quality(data, day)
    except weather.WeatherError:
        val, _ = cache_mod.read(cache, pk)
        if val:
            return {int(h): tuple(v) for h, v in val.items()}, "stale"
        raise
    cache_mod.write(cache, pk, {str(h): list(v) for h, v in hourly.items()}, FRESH_S)
    return hourly, "live"
