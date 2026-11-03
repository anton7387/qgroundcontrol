#!/usr/bin/env python3
"""Pixel-diff two screenshot sets produced by the VectorNav harness (custom/src/VectorNavScreenshots.cc).

    screenshot-diff.py <baseline-dir> <candidate-dir> [--out <dir>] [--tolerance N]

For every <scene>.png in the baseline, compares it with the candidate's file of the same name and prints one line per
image: the scene, the number of differing pixels, the image size, and the verdict. A pixel differs when any channel
differs by more than --tolerance (default 0, exact). Regions listed in <scene>.mask.json (written by the harness: the
scene rectangles of every map item, whose tiles come from the network and are not reproducible) are excluded from the
count and reported separately. With --out, a difference image (differing pixels in red on a dimmed baseline) is written
per scene that differs. Exit status: 0 when every image has 0 differing pixels outside the masks and the two sets hold
the same scene names, 1 otherwise. Needs Pillow (python3-pil, in upstream's install_dependencies list).
"""
import argparse
import json
import pathlib
import sys

from PIL import Image, ImageChops


def load_mask(path: pathlib.Path):
    if not path.exists():
        return []
    with path.open() as f:
        data = json.load(f)
    rects = []
    for r in data.get("masks", []):
        rects.append((int(r["x"]), int(r["y"]), int(r["x"]) + int(r["width"]), int(r["y"]) + int(r["height"])))
    return rects


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("baseline", type=pathlib.Path)
    ap.add_argument("candidate", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, default=None, help="write difference images here")
    ap.add_argument("--tolerance", type=int, default=0, help="per-channel difference that still counts as equal")
    args = ap.parse_args()

    base_files = sorted(p for p in args.baseline.glob("*.png"))
    cand_names = {p.name for p in args.candidate.glob("*.png")}
    base_names = {p.name for p in base_files}
    ok = True
    if base_names != cand_names:
        ok = False
        for name in sorted(base_names - cand_names):
            print(f"{name[:-4]:32s} MISSING in candidate")
        for name in sorted(cand_names - base_names):
            print(f"{name[:-4]:32s} EXTRA in candidate")
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)

    print(f"{'scene':32s} {'differing':>9s} {'masked':>9s} {'size':>11s}  verdict")
    for base_path in base_files:
        cand_path = args.candidate / base_path.name
        if not cand_path.exists():
            continue
        scene = base_path.stem
        a = Image.open(base_path).convert("RGB")
        b = Image.open(cand_path).convert("RGB")
        if a.size != b.size:
            ok = False
            print(f"{scene:32s} {'-':>9s} {'-':>9s} {a.size[0]}x{a.size[1]}  SIZE DIFFERS ({b.size[0]}x{b.size[1]})")
            continue
        diff = ImageChops.difference(a, b)
        if args.tolerance > 0:
            diff = diff.point(lambda v: 255 if v > args.tolerance else 0)
        # One byte per pixel: 0 where equal in all channels.
        changed = diff.convert("L").point(lambda v: 255 if v else 0)
        masks = load_mask(base_path.with_suffix(".mask.json"))
        masked_count = 0
        if masks:
            for (x0, y0, x1, y1) in masks:
                region = changed.crop((x0, y0, x1, y1))
                masked_count += sum(1 for v in region.getdata() if v)
                changed.paste(0, (x0, y0, x1, y1))
        count = sum(1 for v in changed.getdata() if v)
        verdict = "same" if count == 0 else "DIFFERS"
        if count:
            ok = False
            if args.out:
                dim = Image.blend(a, Image.new("RGB", a.size, (0, 0, 0)), 0.6)
                red = Image.new("RGB", a.size, (255, 0, 0))
                dim.paste(red, mask=changed)
                dim.save(args.out / f"{scene}.diff.png")
        print(f"{scene:32s} {count:9d} {masked_count:9d} {a.size[0]:5d}x{a.size[1]:<5d}  {verdict}")
    print("RESULT:", "0 differing pixels per image outside the masks" if ok else "differences found")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
