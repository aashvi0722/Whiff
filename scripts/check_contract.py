#!/usr/bin/env python3
"""Validate /contract/*.sample.json against the Whiff contract v1 (stdlib only).
Run from the repo root:  python3 scripts/check_contract.py
Later you can import check_response() to validate real API output too."""
import json, glob, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
REG = json.load(open(os.path.join(ROOT, "contract", "reason_codes.json"), encoding="utf-8"))
E = REG["enums"]
CODES = {c["code"]: c["params"] for c in REG["reason_codes"]}

def band_of(a):
    return ("good" if a <= 50 else "satisfactory" if a <= 100 else "moderate" if a <= 200
            else "poor" if a <= 300 else "very_poor" if a <= 400 else "severe")

def need(d, keys, where, errs):
    for k in keys:
        if k not in d:
            errs.append(f"{where}: missing '{k}'")

def check_codes(lst, where, errs):
    for rc in lst:
        c = rc.get("code")
        if c not in CODES:
            errs.append(f"{where}: unknown reason code '{c}'"); continue
        missing = [p for p in CODES[c] if p not in rc.get("params", {})]
        if missing:
            errs.append(f"{where}: code '{c}' missing params {missing}")

def check_smoke(d, errs):
    need(d, ["contract_version","mode","replay","location","generated_at","risk","arrival_hours",
             "arrival_range_hours","confidence","confidence_reasons","sources","wind","festival",
             "reason_codes","data_quality"], "smoke", errs)
    if d.get("risk") not in E["risk"]: errs.append("smoke: bad risk")
    if d.get("confidence") not in E["confidence"]: errs.append("smoke: bad confidence")
    if d.get("mode") not in E["mode"]: errs.append("smoke: bad mode")
    if (d.get("mode") == "replay") != (d.get("replay") is not None):
        errs.append("smoke: replay object must exist iff mode == replay")
    if d.get("risk") == "none":
        if d.get("arrival_hours") is not None or d.get("arrival_range_hours") is not None:
            errs.append("smoke: risk none must have null arrival fields")
    else:
        a, r = d.get("arrival_hours"), d.get("arrival_range_hours")
        if a is None or r is None or not (r[0] <= a <= r[1]):
            errs.append("smoke: arrival_hours must sit inside arrival_range_hours")
    for s in d.get("sources", []):
        need(s, ["type","region_code","fire_count","distance_km","bearing_deg","travel_hours"], "smoke.source", errs)
        if s.get("type") not in E["source_type"]: errs.append("smoke.source: bad type")
    for c in d.get("confidence_reasons", []):
        if c not in REG["confidence_reasons"]: errs.append(f"smoke: unknown confidence reason '{c}'")
    if d.get("data_quality", {}).get("served_from") not in E["served_from"]: errs.append("smoke: bad served_from")
    check_codes(d.get("reason_codes", []), "smoke.reason_codes", errs)

def check_day(d, errs):
    need(d, ["contract_version","date","audience","location","day_state","aqi_is_estimate","hours","windows",
             "best_hour","worst_hour","day_avg_pm25","exposure_avoided_hours","cigarette_equiv",
             "reason_codes","advice_codes","data_quality"], "day", errs)
    if d.get("audience") not in E["audience"]: errs.append("day: bad audience")
    if d.get("day_state") not in E["day_state"]: errs.append("day: bad day_state")
    hrs = d.get("hours", [])
    hs = [h["h"] for h in hrs]
    if hs != sorted(set(hs)) or any(h < 5 or h > 22 for h in hs):
        errs.append("day: hours must be unique, increasing, within 5..22")
    mh = d.get("data_quality", {}).get("missing_hours")
    if mh is None or len(hs) + mh != 18:
        errs.append("day: data_quality.missing_hours must equal 18 minus the number of hours")
    for h in hrs:
        if h["band"] != band_of(h["aqi"]): errs.append(f"day: hour {h['h']} band does not match aqi")
        if h["status"] not in E["hour_status"]: errs.append(f"day: hour {h['h']} bad status")
    if [w["rank"] for w in d.get("windows", [])] != list(range(1, len(d.get("windows", [])) + 1)):
        errs.append("day: window ranks must be 1..n in order")
    st = d.get("day_state")
    if st == "windows" and not d.get("windows"): errs.append("day: windows state needs windows")
    if st in ("caution", "stay_in") and d.get("windows"): errs.append("day: caution/stay_in must have no windows")
    if st == "stay_in" and any(h["status"] != "stay" for h in hrs if h["h"] <= 21):
        errs.append("day: stay_in needs every active hour = stay")
    if d.get("cigarette_equiv", {}).get("approx") is not True: errs.append("day: cigarette_equiv.approx must be true")
    for w in d.get("windows", []):
        check_codes(w.get("reason_codes", []), "day.window", errs)
    check_codes(d.get("reason_codes", []), "day.reason_codes", errs)
    for a in d.get("advice_codes", []):
        if a not in REG["advice_codes"]: errs.append(f"day: unknown advice code '{a}'")

def check_history(d, errs):
    need(d, ["contract_version","worst_day","days","data_quality"], "history", errs)
    w = d.get("worst_day") or {}
    need(w, ["date","peak_pm25","band","likely_cause","cause_confidence"], "history.worst_day", errs)
    if w.get("likely_cause") not in E["likely_cause"]: errs.append("history: bad likely_cause")
    for x in d.get("days", []):
        if x["band"] not in E["band"]: errs.append("history: bad band")

def check_replays(d, errs):
    need(d, ["contract_version","events"], "replays", errs)
    for e in d.get("events", []):
        need(e, ["event_id","city","label_key","as_of"], "replays.event", errs)

def check_error(d, errs):
    need(d, ["contract_version","error"], "error", errs)
    if d.get("error", {}).get("code") not in E["error_code"]: errs.append("error: bad code")

def check_response(kind, d):
    errs = []
    if d.get("contract_version") != 1: errs.append("contract_version must be 1")
    {"smoke": check_smoke, "day": check_day, "history": check_history,
     "replays": check_replays, "error": check_error}[kind](d, errs)
    return errs

def main():
    bad = 0
    files = sorted(glob.glob(os.path.join(ROOT, "contract", "*.sample.json")))
    for f in files:
        name = os.path.basename(f)
        kind = name.split("_")[0].split(".")[0]
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception as ex:
            print(f"FAIL {name}: invalid JSON ({ex})"); bad += 1; continue
        errs = check_response(kind, d)
        if errs:
            bad += 1; print(f"FAIL {name}")
            for e in errs: print("   -", e)
        else:
            print(f"ok   {name}")
    print(f"\n{len(files)-bad}/{len(files)} samples valid")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
