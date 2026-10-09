"""Hourly job (EventBridge): refresh India's fire clusters, then precompute /smoke and air-quality
results for the configured cities, so the app answers from cache and upstream APIs are not hammered."""
import json
import os
from datetime import datetime, timezone

from lib import cache as cache_mod, service, smoke_logic

_CITIES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "cities.json")


def handler(event, context):
    now = datetime.now(timezone.utc)
    cache = cache_mod.get_cache()
    key = os.environ.get("FIRMS_KEY", "")
    out = {"fire_cells": 0, "smoke_results": 0, "air_series": 0, "errors": []}

    cells, newest, src, stale = service.get_fires(cache, key, now, force_refresh=True)   # raises if FIRMS is down and nothing is cached
    out["fire_cells"] = len(cells)
    out["fires_from"] = src
    today = now.astimezone(smoke_logic.IST).date()
    with open(_CITIES, encoding="utf-8") as f:
        cities = json.load(f)["cities"]
    for c in cities:
        try:
            service.compute_smoke(c["lat"], c["lon"], now, cache, key, recompute=True)   # fires were just refreshed, so they come from cache
            out["smoke_results"] += 1
        except Exception as e:
            out["errors"].append(f"smoke {c['id']}: {type(e).__name__}")
        try:
            service.get_hourly(cache, c["lat"], c["lon"], today, force=True)
            out["air_series"] += 1
        except Exception as e:
            out["errors"].append(f"air {c['id']}: {type(e).__name__}")
    print(f"ingest ok: {out['fire_cells']} fire cells stored, {out['smoke_results']} smoke results, "
          f"{out['air_series']} air-quality series, {len(out['errors'])} errors {out['errors']}")
    return out
