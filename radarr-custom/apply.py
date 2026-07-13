#!/usr/bin/env python3
"""
Apply Radarr custom formats + quality profiles that Recyclarr cannot manage.

Recyclarr can only sync custom formats that exist in the TRaSH Guides (by
trash_id). The YIFY / "Non-YIFY 2160p" formats are hand-made, so they live here
instead and are applied via the Radarr API. This script is idempotent: it
creates missing objects and updates existing ones (matched by name).

Custom format scores in the profile are stored by NAME and resolved to the live
format IDs at apply time, so the profile stays correct across environments.

Usage:
    RADARR_URL=http://localhost:7878 RADARR_API_KEY=xxxx python3 apply.py
    # or rely on ../.env (RADARR_API_KEY) with default URL http://localhost:7878
"""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).parent
URL = os.environ.get("RADARR_URL", "http://localhost:7878").rstrip("/")
KEY = os.environ.get("RADARR_API_KEY")

if not KEY:
    envf = HERE.parent / ".env"
    if envf.exists():
        for line in envf.read_text().splitlines():
            if line.startswith("RADARR_API_KEY="):
                KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
if not KEY:
    sys.exit("RADARR_API_KEY not set (env or ../.env)")


def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(f"{URL}/api/v3/{path}", data=data, method=method,
                               headers={"X-Api-Key": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r) as resp:
            return json.load(resp) if resp.length != 0 else None
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} failed: {e.code} {e.read().decode()[:400]}")


def apply_custom_format(defn):
    existing = {c["name"]: c for c in req("GET", "customformat")}
    if defn["name"] in existing:
        cur = existing[defn["name"]]
        payload = dict(defn, id=cur["id"])
        req("PUT", f"customformat/{cur['id']}", payload)
        print(f"  updated CF  {defn['name']} (id {cur['id']})")
    else:
        new = req("POST", "customformat", defn)
        print(f"  created CF  {defn['name']} (id {new['id']})")


def apply_profile(defn):
    scores = defn.pop("customFormatScores", {})
    cfs = {c["name"]: c["id"] for c in req("GET", "customformat")}
    defn["formatItems"] = [{"format": cid, "name": name, "score": scores.get(name, 0)}
                           for name, cid in cfs.items()]
    profiles = {p["name"]: p for p in req("GET", "qualityprofile")}
    if defn["name"] in profiles:
        pid = profiles[defn["name"]]["id"]
        req("PUT", f"qualityprofile/{pid}", dict(defn, id=pid))
        print(f"  updated profile {defn['name']} (id {pid})")
    else:
        new = req("POST", "qualityprofile", defn)
        print(f"  created profile {defn['name']} (id {new['id']})")


def apply_quality_definitions(defs):
    live = {d["quality"]["name"]: d for d in req("GET", "qualitydefinition")}
    n = 0
    for d in defs:
        cur = live.get(d["quality"])
        if not cur:
            continue
        for k in ("minSize", "maxSize", "preferredSize"):
            cur[k] = d.get(k)
        req("PUT", f"qualitydefinition/{cur['id']}", cur)
        n += 1
    print(f"  applied {n} quality definitions (min sizes)")


def main():
    print("Custom formats:")
    for f in sorted((HERE / "custom-formats").glob("*.json")):
        apply_custom_format(json.loads(f.read_text()))
    qd = HERE / "quality-definitions.json"
    if qd.exists():
        print("Quality definitions:")
        apply_quality_definitions(json.loads(qd.read_text()))
    print("Quality profiles:")
    for f in sorted((HERE / "quality-profiles").glob("*.json")):
        apply_profile(json.loads(f.read_text()))
    print("Done.")


if __name__ == "__main__":
    main()
