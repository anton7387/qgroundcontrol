#!/usr/bin/env python3
"""Override-drift check for the VectorNav overlay (VECTORNAV-GCS-PLAN.md item 1.7; run from the repository root).

    check-overrides.py [--since <ref>] [--record]

1. Every QML file the overlay shadows (custom.qrc entries under the /Custom/qml prefix, alias
   QGroundControl/<Module>/<File>.qml) must still exist upstream as src/**/<File>.qml, exactly once; its SHA-256 is
   printed so a change upstream since the override was written is visible.
2. Every patches/*.patch must apply (git apply --check).
3. src/QmlControls/QGCPalette.h and src/QmlControls/ScreenTools.qml are hashed and compared with
   custom/tools/upstream-hashes.json (written with --record at the last merge); a difference means a new upstream
   colour name or metric for the token generator (plan 3.1).
4. The upstream commits since --since (default: the merge-base with upstream's Stable_V5.1 when that ref exists,
   else the tag v5.1.5) that touch the flight-critical areas of VECTORNAV-GCS-EVALUATION.md section 7 are listed for
   the operator's read.
Exit status 0 when 1 to 3 hold (4 is informational), 1 otherwise.
"""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
HASH_FILE = ROOT / "custom" / "tools" / "upstream-hashes.json"
WATCHED = ["src/QmlControls/QGCPalette.h", "src/QmlControls/ScreenTools.qml"]
FLIGHT_CRITICAL = [
    "src/Comms", "src/MAVLink", "src/Vehicle", "src/MissionManager", "src/FactSystem", "src/FirmwarePlugin",
    "src/FlyView/GuidedActionsController.qml", "src/FlyView/GuidedActionConfirm.qml",
    "src/QmlControls/QGCDelayButton.qml",
]


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=False, capture_output=True, text=True).stdout.strip()


def overlay_qml_overrides():
    qrc = ROOT / "custom" / "custom.qrc"
    if not qrc.exists():
        return []
    tree = ET.parse(qrc)
    out = []
    for res in tree.getroot().findall("qresource"):
        if res.get("prefix", "") != "/Custom/qml":
            continue
        for f in res.findall("file"):
            alias = f.get("alias") or f.text
            out.append((alias, f.text))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", default=None, help="upstream ref the fork was last merged with")
    ap.add_argument("--record", action="store_true", help="write the watched files' hashes as the new reference")
    args = ap.parse_args()
    ok = True

    print("== 1. overridden QML files still exist upstream")
    overrides = overlay_qml_overrides()
    if not overrides:
        print("   (no /Custom/qml overrides in custom/custom.qrc)")
    for alias, source in overrides:
        name = pathlib.PurePosixPath(alias).name
        candidates = sorted(p for p in (ROOT / "src").rglob(name))
        if len(candidates) != 1:
            ok = False
            print(f"   FAIL {alias}: {len(candidates)} upstream candidates for {name}: {[str(c.relative_to(ROOT)) for c in candidates]}")
            continue
        print(f"   ok   {alias} <- {candidates[0].relative_to(ROOT)} sha256 {sha256(candidates[0])[:16]} (override {source})")

    print("== 2. patches apply")
    patches = sorted((ROOT / "patches").glob("*.patch")) if (ROOT / "patches").exists() else []
    if not patches:
        print("   (no patches/)")
    for p in patches:
        r = subprocess.run(["git", "apply", "--check", str(p)], cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            ok = False
            print(f"   FAIL {p.name}: {r.stderr.strip()}")
        else:
            print(f"   ok   {p.name}")

    print("== 3. watched upstream files (token sources)")
    current = {w: sha256(ROOT / w) for w in WATCHED if (ROOT / w).exists()}
    for w in WATCHED:
        if w not in current:
            ok = False
            print(f"   FAIL {w}: missing")
    recorded = json.loads(HASH_FILE.read_text()) if HASH_FILE.exists() else {}
    for w, h in current.items():
        if args.record:
            print(f"   rec  {w} {h[:16]}")
        elif w not in recorded:
            ok = False
            print(f"   FAIL {w}: no recorded hash (run with --record at the merge)")
        elif recorded[w] != h:
            ok = False
            print(f"   DRIFT {w}: recorded {recorded[w][:16]} now {h[:16]} (review for new colour names or metrics)")
        else:
            print(f"   ok   {w} {h[:16]}")
    if args.record:
        HASH_FILE.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
        print(f"   wrote {HASH_FILE.relative_to(ROOT)}")

    print("== 4. upstream commits touching flight-critical areas since the last merge")
    since = args.since
    if since is None:
        base = git("merge-base", "HEAD", "upstream/Stable_V5.1")
        since = base if base else "v5.1.5"
    log = git("log", "--oneline", f"{since}..HEAD", "--", *FLIGHT_CRITICAL)
    print(f"   since {since}: {len(log.splitlines())} commit(s)")
    for line in log.splitlines():
        print(f"   {line}")

    print("RESULT:", "clean" if ok else "findings above")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
