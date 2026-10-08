"""GET /smoke?lat&lon  (real logic, S2).
?scenario= and ?replay= keep returning contract samples (demo and testing aids)."""
import os
import time
from datetime import datetime, timezone

from lib import firms, weather, smoke_logic, festival
from lib.stub import serve, respond

CACHE_TTL_S = 15 * 60
_CACHE = {"t": 0.0, "cells": None, "age": None}   # per warm Lambda container; DynamoDB cache comes with the ingest job


def _err(status, code, retry=None):
    err = {"code": code}
    if retry:
        err["retry_after_s"] = retry
    return respond(status, {"contract_version": 1, "error": err})


def _fires(now_utc):
    """Return (cells, fire_age_hours, served_from). Raises FirmsError if no source answers."""
    if _CACHE["cells"] is not None and time.time() - _CACHE["t"] < CACHE_TTL_S:
        return _CACHE["cells"], _CACHE["age"], "cache"
    fires, errors = firms.fetch_fires(os.environ.get("FIRMS_KEY", ""), now_utc)
    if errors:
        print("FIRMS partial errors:", len(errors))
    cells = firms.cluster(fires, now_utc)
    age = firms.newest_age_hours(fires, now_utc)
    age = 0 if age is None else age
    _CACHE.update(t=time.time(), cells=cells, age=age)
    return cells, age, "live"


def compute_live(lat, lon, now_utc):
    cells, age, served_from = _fires(now_utc)
    now_ist = now_utc.astimezone(smoke_logic.IST)
    wind = weather.fetch_wind(lat, lon, now_ist.replace(tzinfo=None))
    return smoke_logic.build_smoke(
        lat, lon, festival.city_label(lat, lon), cells, wind, now_utc, age,
        festival=festival.festival_for(now_ist.date()), served_from=served_from)


def handler(event, context):
    q = (event or {}).get("queryStringParameters") or {}
    if q.get("scenario") or q.get("replay"):
        return serve(event, "smoke", "smoke_high")
    try:
        lat, lon = float(q["lat"]), float(q["lon"])
    except (KeyError, ValueError, TypeError):
        return _err(400, "invalid_location")
    if not (6 <= lat <= 37 and 68 <= lon <= 98):
        return _err(400, "invalid_location")
    try:
        return respond(200, compute_live(round(lat, 2), round(lon, 2), datetime.now(timezone.utc)))
    except Exception as e:  # never leak a stack trace or the key
        msg = str(e)
        key = os.environ.get("FIRMS_KEY", "")
        if key:
            msg = msg.replace(key, "***")
        print("smoke error:", type(e).__name__, msg[:200])
        return _err(503, "upstream_unavailable", 60)
