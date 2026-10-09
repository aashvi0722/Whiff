#!/usr/bin/env python3
"""Copy /contract/*.sample.json into backend/samples/ so they ship inside the Lambda package.
Run before every `sam build`. backend/samples/ is git-ignored."""
import glob, os, shutil

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
dest = os.path.join(root, "backend", "samples")
shutil.rmtree(dest, ignore_errors=True)   # never keep stale copies
os.makedirs(dest, exist_ok=True)
n = 0
for f in glob.glob(os.path.join(root, "contract", "*.sample.json")):
    shutil.copy(f, dest); n += 1
print(f"copied {n} samples to backend/samples/")
