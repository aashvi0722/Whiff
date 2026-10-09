"""GET /day?lat&lon&audience=general|sensitive|child|outdoor&wake_h=  (real logic, S3).
?scenario= and ?replay= keep returning contract samples."""
from datetime import datetime, timezone

from lib import cache as cache_mod, service, day_logic, festival, smoke_logic
from lib.stub import serve, respond
from lib.api import error_response as _err, parse_location
from lib.bands import AUDIENCES


def _hourly(lat, lon, day):
    return service.get_hourly(cache_mod.get_cache(), lat, lon, day)


def compute_day(lat, lon, audience, wake_h, now_utc):
    day = now_utc.astimezone(smoke_logic.IST).date()
    hourly, src = _hourly(lat, lon, day)
    return day_logic.build_day(
        hourly, audience, day.isoformat(),
        {"lat": lat, "lon": lon, "label": festival.city_label(lat, lon)},
        wake_h=wake_h, served_from="cache" if src == "stale" else src, stale=(src == "stale"))


def handler(event, context):
    q = (event or {}).get("queryStringParameters") or {}
    if q.get("scenario") or q.get("replay"):
        return serve(event, "day", "day_windows")
    loc = parse_location(q)
    if loc is None:
        return _err(400, "invalid_location")
    audience = q.get("audience") if q.get("audience") in AUDIENCES else "general"
    try:
        wake_h = int(q["wake_h"]) if q.get("wake_h") else None
    except ValueError:
        wake_h = None
    try:
        return respond(200, compute_day(loc[0], loc[1], audience, wake_h, datetime.now(timezone.utc)))
    except Exception as e:
        print("day error:", type(e).__name__, str(e)[:200])
        return _err(503, "upstream_unavailable", 60)
