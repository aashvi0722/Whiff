"""Serves the built frontend (a single-page app) from a private S3 bucket, behind the same HTTPS API.
Deploy the app with scripts/deploy-frontend.ps1 (just an S3 upload; no stack update needed)."""
import base64
import gzip
import mimetypes
import os
import time
import urllib.parse

BUCKET = os.environ.get("BUCKET", "")
_TYPES = {".js": "text/javascript; charset=utf-8", ".mjs": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
          ".html": "text/html; charset=utf-8", ".json": "application/json", ".webmanifest": "application/manifest+json",
          ".svg": "image/svg+xml", ".ico": "image/x-icon", ".woff2": "font/woff2", ".txt": "text/plain; charset=utf-8",
          ".map": "application/json"}
_TEXT = ("text/", "application/json", "application/manifest+json", "image/svg+xml", "application/javascript")
_MEM = {}          # key -> (loaded_at, body)
_TTL_S = 30        # non-hashed files (index.html, sw.js, manifest) are re-read at most every 30 s
_client = {}


def _fetch(key):
    """Return the object's bytes, or None if it does not exist."""
    now = time.time()
    hit = _MEM.get(key)
    if hit and (key.startswith("assets/") or now - hit[0] < _TTL_S):
        return hit[1]
    try:
        if "c" not in _client:
            import boto3
            _client["c"] = boto3.client("s3")
        body = _client["c"].get_object(Bucket=BUCKET, Key=key)["Body"].read()
    except Exception as e:   # NoSuchKey and anything else: treat as missing, never leak details
        if type(e).__name__ not in ("NoSuchKey", "ClientError"):
            print("app fetch error:", type(e).__name__)
        return None
    if len(_MEM) > 200:
        _MEM.clear()
    _MEM[key] = (now, body)
    return body


def _content_type(key):
    ext = os.path.splitext(key)[1].lower()
    return _TYPES.get(ext) or mimetypes.guess_type(key)[0] or "application/octet-stream"


def _reply(status, body, ctype, cache, accept_encoding=""):
    headers = {"Content-Type": ctype, "Cache-Control": cache, "X-Content-Type-Options": "nosniff"}
    is_text = ctype.startswith(_TEXT)
    if is_text and "gzip" in accept_encoding and len(body) > 1024:
        body, headers["Content-Encoding"] = gzip.compress(body), "gzip"
        is_text = False
    if is_text:
        return {"statusCode": status, "headers": headers, "body": body.decode("utf-8", "replace")}
    return {"statusCode": status, "headers": headers, "isBase64Encoded": True,
            "body": base64.b64encode(body).decode("ascii")}


def handler(event, context):
    path = urllib.parse.unquote((event or {}).get("rawPath") or "/")
    enc = ((event or {}).get("headers") or {}).get("accept-encoding", "")
    if ".." in path or "\\" in path or "\x00" in path or len(path) > 200:
        return _reply(400, b"bad path", "text/plain; charset=utf-8", "no-store")
    key = path.lstrip("/") or "index.html"
    body = _fetch(key)
    if body is None:
        if key != "index.html" and "." in key.rsplit("/", 1)[-1]:   # a missing file (e.g. /missing.js)
            return _reply(404, b"not found", "text/plain; charset=utf-8", "no-store")
        key, body = "index.html", _fetch("index.html")          # single-page app: unknown route loads the app
        if body is None:
            return _reply(404, b"Whiff app not uploaded yet. Run scripts/deploy-frontend.ps1", "text/plain; charset=utf-8", "no-store")
    cache = "public, max-age=31536000, immutable" if key.startswith("assets/") else "no-cache"
    return _reply(200, body, _content_type(key), cache, enc)
