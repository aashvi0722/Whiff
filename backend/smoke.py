"""GET /smoke?lat&lon  (real logic; cache-first via DynamoDB, stale-on-failure).
?scenario= and ?replay= keep returning contract samples (demo and testing aids)."""
import os
from datetime import datetime, timezone

from lib import cache as cache_mod, service
from lib.stub import serve, respond
from lib.api import error_response as _err, parse_location


def compute_live(lat, lon, now_utc):
    return service.compute_smoke(lat, lon, now_utc, cache_mod.get_cache(), os.environ.get("FIRMS_KEY", ""))


def handler(event, context):
    q = (event or {}).get("queryStringParameters") or {}
    if q.get("scenario") or q.get("replay"):
        return serve(event, "smoke", "smoke_high")
    loc = parse_location(q)
    if loc is None:
        return _err(400, "invalid_location")
    lat, lon = loc
    try:
        return respond(200, compute_live(lat, lon, datetime.now(timezone.utc)))
    except Exception as e:  # never leak a stack trace or the key
        msg = str(e)
        key = os.environ.get("FIRMS_KEY", "")
        if key:
            msg = msg.replace(key, "***")
        print("smoke error:", type(e).__name__, msg[:200])
        return _err(503, "upstream_unavailable", 60)
