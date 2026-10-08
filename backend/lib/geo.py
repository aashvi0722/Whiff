"""Geometry helpers: distance, bearing, circular statistics, grid cells, rough regions."""
import math

R_KM = 6371.0088


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_KM * math.asin(min(1.0, math.sqrt(a)))


def bearing_deg(lat1, lon1, lat2, lon2):
    """Initial compass bearing (0=N, 90=E) from point 1 to point 2."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def angle_diff(a, b):
    """Smallest absolute difference between two compass angles, 0..180."""
    d = abs(a - b) % 360
    return d if d <= 180 else 360 - d


def circular_mean(angles, weights=None):
    """Return (mean_angle_deg, r) where r in 0..1 is the mean resultant length (1 = all identical)."""
    if not angles:
        return 0.0, 0.0
    if weights is None:
        weights = [1.0] * len(angles)
    sx = sum(w * math.sin(math.radians(a)) for a, w in zip(angles, weights))
    sy = sum(w * math.cos(math.radians(a)) for a, w in zip(angles, weights))
    tw = sum(weights)
    if tw <= 0:
        return 0.0, 0.0
    return (math.degrees(math.atan2(sx, sy)) + 360) % 360, min(1.0, math.hypot(sx, sy) / tw)


def circular_spread_deg(r):
    """Circular standard deviation in degrees from the mean resultant length."""
    r = min(max(r, 1e-9), 1.0)
    return min(180.0, math.degrees(math.sqrt(-2 * math.log(r))))


def cell_center(lat, lon, size=0.25):
    return (round(math.floor(lat / size) * size + size / 2, 4),
            round(math.floor(lon / size) * size + size / 2, 4))


def region_code(lat, lon):
    """VERY rough boxes (not official boundaries). Only used for the 'crop residue likely' label."""
    if 29.5 <= lat <= 32.6 and 73.8 <= lon <= 76.95:
        return "IN-PB"
    if 27.6 <= lat <= 31.0 and 74.4 <= lon <= 77.6:
        return "IN-HR"
    if 26.4 <= lat <= 30.2 and 77.0 <= lon <= 79.6:
        return "IN-UP"
    return "IN"
