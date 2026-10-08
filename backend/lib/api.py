"""Small shared helpers for the HTTP handlers."""
from .stub import respond


def error_response(status, code, retry=None):
    err = {"code": code}
    if retry:
        err["retry_after_s"] = retry
    return respond(status, {"contract_version": 1, "error": err})


def parse_location(q):
    """Return (lat, lon) inside India's box, or None if missing, non-numeric, NaN or out of range."""
    try:
        lat, lon = float(q["lat"]), float(q["lon"])
    except (KeyError, ValueError, TypeError):
        return None
    if not (6 <= lat <= 37 and 68 <= lon <= 98):
        return None
    return round(lat, 2), round(lon, 2)
