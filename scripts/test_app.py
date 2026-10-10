#!/usr/bin/env python3
"""Offline tests for the frontend-serving Lambda (S3 replaced by a dict). Run: python scripts/test_app.py"""
import base64, gzip, os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "backend"))
import app   # noqa: E402

fails = 0
def expect(label, ok, extra=""):
    global fails
    print(("ok   " if ok else "FAIL ") + label + (f"   {extra}" if not ok and extra else ""))
    fails += 0 if ok else 1

FILES = {"index.html": b"<!doctype html><title>Whiff</title>", "assets/index-abc123.js": b"console.log(1);" * 200,
         "assets/logo.png": bytes(range(256)), "manifest.webmanifest": b'{"name":"Whiff"}', "sw.js": b"//sw"}
app._fetch = lambda key: FILES.get(key)
def call(path, enc=""):
    return app.handler({"rawPath": path, "headers": {"accept-encoding": enc} if enc else {}}, None)

r = call("/")
expect("root serves index.html, no-cache", r["statusCode"] == 200 and "Whiff" in r["body"] and r["headers"]["Cache-Control"] == "no-cache" and r["headers"]["Content-Type"].startswith("text/html"))
r = call("/assets/index-abc123.js")
expect("hashed asset: JS type, immutable year-long cache", r["statusCode"] == 200 and r["headers"]["Content-Type"].startswith("text/javascript") and "immutable" in r["headers"]["Cache-Control"])
r = call("/assets/index-abc123.js", "gzip, br")
expect("large text is gzipped when the browser accepts it", r["headers"].get("Content-Encoding") == "gzip" and r["isBase64Encoded"] and gzip.decompress(base64.b64decode(r["body"])) == FILES["assets/index-abc123.js"])
r = call("/assets/logo.png")
expect("binary files are base64 and round-trip exactly", r["isBase64Encoded"] and base64.b64decode(r["body"]) == FILES["assets/logo.png"] and r["headers"]["Content-Type"] == "image/png")
r = call("/manifest.webmanifest")
expect("web manifest has the right type", r["headers"]["Content-Type"] == "application/manifest+json")
r = call("/radar")
expect("unknown route loads the app (single-page fallback)", r["statusCode"] == 200 and "Whiff" in r["body"])
r = call("/missing.js")
expect("missing file with an extension is a real 404", r["statusCode"] == 404)
for bad in ("/../etc/passwd", "/a/../../b", "/%2e%2e/secret", "/a\\b", "/x" * 120):
    expect(f"unsafe path rejected: {bad[:24]!r}", call(bad)["statusCode"] == 400, call(bad)["statusCode"])
expect("security header set", call("/")["headers"]["X-Content-Type-Options"] == "nosniff")
FILES.clear()
r = call("/")
expect("before the first upload: a helpful 404, not a crash", r["statusCode"] == 404 and "not uploaded" in r["body"])
print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
