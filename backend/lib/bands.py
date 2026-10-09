"""AQI conversion and per-audience thresholds (playbook 5.4).
Piecewise-linear through the CPCB breakpoints. VERIFY the breakpoints against the official CPCB table.
Official AQI uses 24 h averages, so hourly AQI here is an ESTIMATE (the contract flags it)."""

PM25_POINTS = [(0, 0), (30, 50), (60, 100), (90, 200), (120, 300), (250, 400), (380, 500)]
PM10_POINTS = [(0, 0), (50, 50), (100, 100), (250, 200), (350, 300), (430, 400), (510, 500)]

# audience -> (go_max_aqi, stay_in_above_aqi or None). Placeholders, not medical limits.
AUDIENCES = {
    "general": (100, 200),
    "sensitive": (50, 100),
    "child": (80, 150),
    "outdoor": (100, None),   # outdoor workers cannot "stay in": hours above go limit are "caution"
}


def _interp(v, points):
    if v <= points[0][0]:
        return 0.0
    for (c0, a0), (c1, a1) in zip(points, points[1:]):
        if v <= c1:
            return a0 + (v - c0) / (c1 - c0) * (a1 - a0)
    return 500.0


def aqi_from(pm25, pm10=None):
    """AQI = the larger of the PM2.5 and PM10 sub-indices (PM10 optional)."""
    subs = [_interp(pm25, PM25_POINTS)]
    if pm10 is not None:
        subs.append(_interp(pm10, PM10_POINTS))
    return round(max(subs))


def band_of(aqi):
    return ("good" if aqi <= 50 else "satisfactory" if aqi <= 100 else "moderate" if aqi <= 200
            else "poor" if aqi <= 300 else "very_poor" if aqi <= 400 else "severe")


def status_for(aqi, audience):
    go, stay = AUDIENCES[audience]
    if aqi <= go:
        return "go"
    if stay is not None and aqi > stay:
        return "stay"
    return "caution"
