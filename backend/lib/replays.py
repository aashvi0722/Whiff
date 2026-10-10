"""Replays of saved past events: backend/replays/<event_id>/{smoke,day}.json, made by scripts/make_replay.py."""
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "replays")
_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")


def load(event_id, kind):
    """Return the saved JSON for an event, or None (also for any unsafe id)."""
    if not isinstance(event_id, str) or not _ID.match(event_id) or kind not in ("smoke", "day"):
        return None
    try:
        with open(os.path.join(ROOT, event_id, f"{kind}.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def list_events():
    """Events with a saved smoke.json, as the /replays contract shape. Empty list if none."""
    out = []
    try:
        names = sorted(os.listdir(ROOT))
    except OSError:
        return out
    for name in names:
        smoke = load(name, "smoke")
        if smoke and smoke.get("replay"):
            r = smoke["replay"]
            out.append({"event_id": r["event_id"], "city": smoke["location"]["label"],
                        "label_key": r["label_key"], "as_of": r["as_of"]})
    return out
