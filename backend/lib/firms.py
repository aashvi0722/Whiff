"""NASA FIRMS: fetch VIIRS fire detections, parse the CSV, cluster into 0.25 degree cells.
Standard library only. The MAP_KEY is never logged or included in error messages."""
import csv
import io
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

from .geo import cell_center, region_code

BASE = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
SOURCES = ["VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT", "VIIRS_NOAA21_NRT"]
INDIA_BBOX = (68, 6, 98, 36)  # west, south, east, north


class FirmsError(Exception):
    pass


def build_url(key, source, bbox=INDIA_BBOX, days=2, date=None):
    area = ",".join(str(x) for x in bbox)
    url = f"{BASE}/{key}/{source}/{area}/{days}"
    return f"{url}/{date}" if date else url


def _scrub(msg, key):
    return msg.replace(key, "***") if key else msg


def fetch_csv(key, source, bbox=INDIA_BBOX, days=2, date=None, timeout=8):
    url = build_url(key, source, bbox, days, date)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:  # network, HTTP error, timeout
        raise FirmsError(_scrub(f"{source}: {type(e).__name__}: {e}", key)) from None


def _keep_confidence(value):
    v = (value or "").strip().lower()
    if v in ("n", "h", "nominal", "high"):
        return True
    try:
        return float(v) >= 30  # numeric confidence (MODIS-style), if ever present
    except ValueError:
        return False


def parse_csv(text):
    """Return [{'lat','lon','frp','t'(aware UTC datetime)}] for nominal/high confidence rows."""
    text = (text or "").strip()
    if not text:
        return []
    reader = csv.DictReader(io.StringIO(text))
    fields = reader.fieldnames or []
    if "latitude" not in fields or "longitude" not in fields:
        raise FirmsError("unexpected FIRMS response: " + text[:80].replace("\n", " "))
    out = []
    for row in reader:
        try:
            if not _keep_confidence(row.get("confidence")):
                continue
            hhmm = (row.get("acq_time") or "0").strip().zfill(4)
            t = datetime.strptime(f"{row['acq_date']} {hhmm}", "%Y-%m-%d %H%M").replace(tzinfo=timezone.utc)
            out.append({"lat": float(row["latitude"]), "lon": float(row["longitude"]),
                        "frp": float(row.get("frp") or 0), "t": t})
        except (KeyError, ValueError):
            continue  # skip malformed rows
    return out


def fetch_fires(key, now=None, sources=SOURCES, bbox=INDIA_BBOX, days=2, timeout=8):
    """Fetch all sources in parallel. Returns (fires, errors).
    Raises FirmsError only if EVERY source failed."""
    def one(source):
        try:
            return parse_csv(fetch_csv(key, source, bbox, days, timeout=timeout)), None
        except FirmsError as e:
            return None, _scrub(str(e), key)

    with ThreadPoolExecutor(max_workers=max(1, len(sources))) as ex:
        results = list(ex.map(one, sources))
    fires = [f for rows, _ in results if rows is not None for f in rows]
    errors = [err for _, err in results if err]
    if all(rows is None for rows, _ in results):
        raise FirmsError("; ".join(errors) or "no FIRMS source answered")
    return fires, errors


def cluster(fires, now, size=0.25):
    """Group detections into grid cells. n24 = last 24 h, nprev = the 24 h before that."""
    cells = {}
    for f in fires:
        age_h = max(0.0, (now - f["t"]).total_seconds() / 3600)
        if age_h > 48:
            continue
        c = cell_center(f["lat"], f["lon"], size)
        d = cells.setdefault(c, {"lat": c[0], "lon": c[1], "n24": 0, "nprev": 0, "frp": 0.0})
        if age_h <= 24:
            d["n24"] += 1
        else:
            d["nprev"] += 1
        d["frp"] += f["frp"]
    out = list(cells.values())
    for d in out:
        d["frp"] = round(d["frp"], 1)
        d["region"] = region_code(d["lat"], d["lon"])
    return sorted(out, key=lambda d: -d["n24"])


def newest_age_hours(fires, now):
    if not fires:
        return None
    return max(0.0, (now - max(f["t"] for f in fires)).total_seconds() / 3600)


def counts_by_region(cells):
    out = {}
    for c in cells:
        out[c["region"]] = out.get(c["region"], 0) + c["n24"]
    return out
