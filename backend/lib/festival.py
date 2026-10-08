"""Festival flag from config/festivals.json (verified dates only; empty until verified)."""
import json
import os
from datetime import date

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "festivals.json")
INACTIVE = {"active": False, "name": None}


def festival_for(today, path=_PATH, window_days=2):
    """Active if a listed firecracker night falls between today and today + window_days."""
    try:
        with open(path, encoding="utf-8") as f:
            nights = json.load(f).get("nights", [])
        for n in nights:
            delta = (date.fromisoformat(n["night"]) - today).days
            if 0 <= delta <= window_days:
                return {"active": True, "name": n["name"]}
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return dict(INACTIVE)


def city_label(lat, lon, path=None, max_km=60):
    """Nearest configured city within max_km, else 'Your location'."""
    from .geo import haversine_km
    path = path or os.path.join(os.path.dirname(_PATH), "cities.json")
    try:
        with open(path, encoding="utf-8") as f:
            cities = json.load(f)["cities"]
        best = min(cities, key=lambda c: haversine_km(lat, lon, c["lat"], c["lon"]))
        if haversine_km(lat, lon, best["lat"], best["lon"]) <= max_km:
            return best["label"]
    except (OSError, ValueError, KeyError):
        pass
    return "Your location"
