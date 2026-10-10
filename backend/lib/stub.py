"""Stub-phase helpers: serve the frozen contract samples.
Honours ?scenario= and ?replay=. Replaced piece by piece by real logic from S2 on."""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_DIRS = [
    os.path.join(_HERE, "..", "..", "contract"),  # running from the repo: always the live contract files
    os.path.join(_HERE, "..", "samples"),         # inside the Lambda package (bundled by sync_samples.py)
]


def _samples_dir():
    for d in _DIRS:
        if os.path.isdir(d) and any(f.endswith(".sample.json") for f in os.listdir(d)):
            return d
    raise FileNotFoundError("contract samples not found; run scripts/sync_samples.py")


def load_sample(name):
    with open(os.path.join(_samples_dir(), f"{name}.sample.json"), encoding="utf-8") as f:
        return json.load(f)


def respond(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def _events():
    """Real saved replays if any exist, otherwise the contract sample list."""
    from . import replays
    return replays.list_events() or load_sample("replays")["events"]


def _known_replay_ids():
    return {e["event_id"] for e in _events()}


def serve(event, kind, default):
    """kind: smoke | day | history | replays. default: sample file name to serve."""
    q = (event or {}).get("queryStringParameters") or {}
    sc = q.get("scenario")

    if sc == "error":
        return respond(503, load_sample("error"))

    replay = q.get("replay")
    if replay and kind in ("smoke", "day"):
        if replay not in _known_replay_ids():
            return respond(404, {"contract_version": 1, "error": {"code": "unknown_replay"}})
        from . import replays
        saved = replays.load(replay, kind)
        if saved is not None:
            return respond(200, saved)
        if kind == "smoke":
            default = "smoke_replay"

    if sc and (sc == kind or sc.startswith(kind + "_")):
        try:
            return respond(200, load_sample(sc))
        except FileNotFoundError:
            pass  # unknown scenario name: fall back to the default
    return respond(200, load_sample(default))
