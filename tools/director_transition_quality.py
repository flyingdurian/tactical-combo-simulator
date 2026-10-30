#!/usr/bin/env python3
"""Read-only transition diagnostics for unapproved pose-order storyboards.

Alpha silhouette geometry only: NOT verified feet, body mechanics, weapon contact,
or visual approval. Does not write to combat data.
"""
from __future__ import annotations
import argparse
from collections import Counter
import html
import json
import math
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def foot_proxy(frame: dict, root: Path, cache: dict) -> dict:
    path = str(frame["pose_path"])
    anchor = frame.get("anchor")
    if not path.startswith("res://") or not isinstance(anchor, list) or len(anchor) != 2:
        raise ValueError("Sprite must have local path and source anchor")
    if path not in cache:
        file = (root / path[6:]).resolve()
        if not file.is_relative_to(root.resolve()):
            raise ValueError("Sprite path escapes project root")
        if not file.is_file():
            raise FileNotFoundError(path)
        with Image.open(file) as im:
            alpha = im.convert("RGBA").getchannel("A")
            bbox = alpha.getbbox()
            if bbox is None:
                raise ValueError("Empty sprite: " + path)
            w, h = alpha.size
            data = alpha.tobytes()
            xs = [n % w for n, a in enumerate(data)
                  if a >= 48 and bbox[3]-6 <= n//w < bbox[3]]
            fx = sorted(xs)[len(xs)//2] if xs else (bbox[0]+bbox[2])/2
            cache[path] = {"foot": (fx, bbox[3]-1),
                           "center": ((bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2)}
    original = cache[path]
    facing = int(frame.get("native_facing", 1))
    offset = frame.get("offset", [0, 0])
    if facing not in (-1, 1) or not isinstance(offset, list) or len(offset) != 2:
        raise ValueError("Invalid pose transform")
    foot = [(original["foot"][0]-anchor[0])*facing + offset[0],
            original["foot"][1]-anchor[1] + offset[1]]
    center = [(original["center"][0]-anchor[0])*facing + offset[0],
              original["center"][1]-anchor[1] + offset[1]]
    return {"foot_local": [round(v, 2) for v in foot],
            "centroid_local": [round(v, 2) for v in center],
            "confidence": "UNVERIFIED_ALPHA_PROXY"}


def analyze(candidate: dict, root: Path) -> dict:
    frames = candidate["frame_track"]
    cache = {}
    proxies = [foot_proxy(frame, root, cache) for frame in frames]
    boundaries = {int(b["start_tick"]) for b in candidate.get("beat_track", [])[1:]}
    pairs = []
    points = 0
    for i in range(1, len(frames)):
        before, after = proxies[i-1], proxies[i]
        dx = round(after["foot_local"][0] - before["foot_local"][0], 2)
        dy = round(after["foot_local"][1] - before["foot_local"][1], 2)
        cx = after["centroid_local"][0] - before["centroid_local"][0]
        cy = after["centroid_local"][1] - before["centroid_local"][1]
        boundary = frames[i]["tick_start"] in boundaries
        donor_change = frames[i]["source_sequence_id"] != frames[i-1]["source_sequence_id"]
        high = abs(dx)>30 or abs(dy)>22 or math.hypot(cx,cy)>48
        medium = abs(dx)>17 or abs(dy)>13 or math.hypot(cx,cy)>30
        risk = "high" if high else ("medium" if medium else "low")
        weight = (3 if high else 1 if medium else 0) * (2 if boundary or donor_change else 1)
        points += weight
        pairs.append({"from_pose":i-1, "to_pose":i, "foot_jump":[dx,dy],
                      "centroid_jump":[round(cx,2), round(cy,2)],
                      "beat_boundary":boundary,"cross_source_move":donor_change,
                      "geometry_risk":risk,"review_weight":weight})
    ticks = sorted(int(h["tick"]) for h in candidate.get("impact_proposals", []))
    close_hits = sum(b-a<5 for a,b in zip(ticks, ticks[1:]))
    duplicates = sum(n-1 for n in Counter(f["pose_path"] for f in frames).values() if n>1)
    points += 2*close_hits + duplicates
    return {"candidate_id":candidate["id"],"duration_ticks":candidate["duration_ticks"],
            "pose_count":len(frames),"hits":len(ticks),"close_hit_pairs":close_hits,
            "duplicate_poses":duplicates, "review_points":points,
            "review_priority":"high" if points>=12 else "medium" if points>=5 else "low",
            "transitions":pairs,"foot_proxies":proxies,
            "visual_verdict":"NOT_ASSESSED — geometry is not artistic acceptance"}


def audit_bank(bank: dict, root: Path) -> dict:
    rows = {key:analyze(candidate,root) for key,candidate in bank["candidates"].items()}
    order = sorted(rows, key=lambda key:(rows[key]["review_points"], key))
    return {"schema":1,"character":bank["character"],"source_sha256":bank["source_sha256"],
            "review_order_lowest_proxy_risk_first":order,"candidates":rows,
            "not_a_best_choreography_ranking":True,"gameplay_modified":False}


def report_html(audit: dict, out: Path) -> None:
    sections = []
    for key in audit["review_order_lowest_proxy_risk_first"]:
        info = audit["candidates"][key]
        rows = "".join(
            "<tr><td>%d → %d</td><td>%s</td><td>%s, %s</td><td>%s</td></tr>" %
            (t["from_pose"],t["to_pose"],t["geometry_risk"],*t["foot_jump"],
             "cross-source" if t["cross_source_move"] else "within-source")
            for t in info["transitions"])
        sections.append("<section><h2>%s</h2><p>Review points: %d · close hits: %d · "
                        "duplicate poses: %d</p><table><tr><th>Join</th><th>Risk</th>"
                        "<th>Foot proxy Δ</th><th>Origin</th></tr>%s</table></section>" %
                        (html.escape(key),info["review_points"],info["close_hit_pairs"],
                         info["duplicate_poses"],rows))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Director join review</title>'
                   '<style>body{font:15px system-ui;background:#101827;color:#eaf1fa;max-width:1050px;'
                   'margin:20px auto;padding:15px}section{border:1px solid #587088;border-radius:12px;'
                   'padding:16px;margin:12px 0}table{border-collapse:collapse;width:100%}'
                   'td,th{border:1px solid #566e83;padding:8px}strong{color:#ffc879}</style>'
                   '<h1>Director join review: '+html.escape(audit["character"])+'</h1>'
                   '<p><strong>UNAPPROVED.</strong> Geometry risk only; no automatic artistic '
                   'selection, contact approval, or live-game replacement.</p>'
                   + "".join(sections) + "</html>", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True, help="Generated role-storyboards parent")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--character", action="append")
    args = p.parse_args()
    for character in args.character or ("chunli", "dante", "kosmos"):
        file = args.source / character / "storyboards.json"
        bank = json.loads(file.read_text())
        result = audit_bank(bank, args.root)
        out = args.out / character
        out.mkdir(parents=True,exist_ok=True)
        (out / "transition_audit.json").write_text(json.dumps(result,indent=2) + "\n")
        report_html(result, out / "transition_report.html")
        print(character, [(key, result["candidates"][key]["review_points"])
                          for key in result["review_order_lowest_proxy_risk_first"]])


if __name__ == "__main__":
    main()
