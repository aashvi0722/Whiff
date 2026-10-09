"""Tiny cache layer. Items: pk, v (JSON string, gzip+base64 when large), exp (fresh until), ttl (DynamoDB cleanup time).
exp and ttl are separate on purpose: DynamoDB TTL deletes late, and we WANT expired items to survive a while
so they can be served as 'stale' when an upstream source is down. Cache failures never break a request."""
import base64
import gzip
import json
import os
import time

KEEP_S = 24 * 3600          # how long an expired item is kept for stale fallback
_GZ_ABOVE = 50_000          # compress values longer than this (DynamoDB items max 400 KB)
_singleton = {}


def encode(value):
    raw = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    if len(raw) <= _GZ_ABOVE:
        return raw
    return "gz:" + base64.b64encode(gzip.compress(raw.encode("utf-8"))).decode("ascii")


def decode(text):
    if text.startswith("gz:"):
        text = gzip.decompress(base64.b64decode(text[3:])).decode("utf-8")
    return json.loads(text)


class MemoryCache:
    """Per-process cache: used locally, in tests, and as the fallback when DynamoDB is unavailable."""
    def __init__(self):
        self.items = {}

    def get(self, pk):
        return self.items.get(pk)

    def put(self, pk, item):
        self.items[pk] = item


class DynamoCache:
    def __init__(self, table_name):
        import boto3   # present in Lambda; imported lazily so local tests do not need it
        self.table = boto3.resource("dynamodb").Table(table_name)

    def get(self, pk):
        return self.table.get_item(Key={"pk": pk}).get("Item")

    def put(self, pk, item):
        self.table.put_item(Item={"pk": pk, **item})


def get_cache():
    if "c" not in _singleton:
        table = os.environ.get("TABLE")
        try:
            _singleton["c"] = DynamoCache(table) if table else MemoryCache()
        except Exception as e:
            print("cache: DynamoDB unavailable, using memory:", type(e).__name__)
            _singleton["c"] = MemoryCache()
    return _singleton["c"]


def read(cache, pk, now=None):
    """Return (value, fresh). (None, False) on a miss or any error."""
    if cache is None:
        return None, False
    try:
        item = cache.get(pk)
        if not item:
            return None, False
        now = time.time() if now is None else now
        return decode(item["v"]), int(item["exp"]) > now
    except Exception as e:
        print("cache read error:", pk.split("#")[0], type(e).__name__)
        return None, False


def write(cache, pk, value, fresh_s, now=None):
    if cache is None:
        return False
    try:
        now = int(time.time() if now is None else now)
        cache.put(pk, {"v": encode(value), "exp": now + fresh_s, "ttl": now + KEEP_S})
        return True
    except Exception as e:
        print("cache write error:", pk.split("#")[0], type(e).__name__)
        return False
