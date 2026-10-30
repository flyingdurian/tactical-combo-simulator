#!/usr/bin/env python3
"""Phase 2: non-destructive sprite-geometry and choreography beat proposals.

The tool measures actual PNG alpha masks but does NOT recognize actions or
prove contact. Every output is an unapproved authoring draft; no combat data
is modified or installed into Godot.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import sys
from pathlib import Path
from statistics import median

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.choreography_director import retime, map_tick, pose_for_tick

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "moves/choreography.json"
STYLES = ("precision", "rush", "weight")


def silhouette(path: Path) -> dict:
    """Report alpha geometry only. A low silhouette point is not verified as a foot."""
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Install Pillow for PNG analysis: pip install pillow") from exc
    with Image.open(path) as im:
        rgba = im.convert("RGBA")
        alpha = rgba.getchannel("A")
        box = alpha.point(lambda n: 255 if n >= 24 else 0).getbbox()
        w, h = rgba.size
        if box is None:
            raise ValueError(f"Blank transparent pose: {path}")
        raw = alpha.tobytes()
        occupied = {k for k, value in enumerate(raw) if value >= 24}
        bottom = box[3] - 1
        xs = [k % w for k in occupied if bottom-3 <= k//w <= bottom]
        foot = [int(median(xs)), bottom] if xs else None
        return {"canvas": [w, h], "bbox": list(box), "visible_area": len(occupied),
                "foot_guess": foot, "foot_confidence": "unverified-bottommost-silhouette",
                "_occupied": occupied}


def scan_move(move: dict, root: Path = ROOT) -> list[dict]:
    result = []
    previous = None
    for i, pose in enumerate(move["poses"]):
        path = pose["path"]
        if not path.startswith("res://"):
            raise ValueError(f"Non-local sprite path: {path}")
        image_path = root / path.removeprefix("res://")
        if not image_path.is_file():
            raise FileNotFoundError(f"Missing sprite: {path}")
        geometry = silhouette(image_path)
        occupied = geometry.pop("_occupied")
        b = geometry["bbox"]
        center = ((b[0]+b[2])/2, (b[1]+b[3])/2)
        if previous is not None and previous["canvas"] == geometry["canvas"]:
            old = previous["occupied"]
            union = len(old | occupied)
            change = round(len(old ^ occupied)/union, 4) if union else 0
            dx = round(center[0]-previous["center"][0], 2)
            dy = round(center[1]-previous["center"][1], 2)
        else:
            change = dx = dy = None
        result.append({"index": i, "pose_path": path, **geometry,
                       "silhouette_change": change, "centroid_delta": [dx, dy],
                       "render_anchor": pose.get("anchor"),
                       "contact_semantics": "unknown", "confidence": "geometry_only"})
        previous = {"canvas": geometry["canvas"], "occupied": occupied, "center": center}
    return result


def stage_suggestions(move: dict, scans: list[dict]) -> list[dict]:
    """Timing association suggests a role, but never approves a pose as contact."""
    hit_poses = {pose_for_tick(move["poses"], int(h["tick"]))[0] for h in move["hit_events"]}
    if not hit_poses:
        raise ValueError("Move has no hit events")
    first, last = min(hit_poses), max(hit_poses)
    roles = []
    for i, scan in enumerate(scans):
        if i in hit_poses:
            label = "candidate_contact"
        elif i < first:
            label = "candidate_anticipation"
        elif i > last:
            label = "candidate_recovery"
        else:
            label = "candidate_transition"
        warnings = []
        delta = scan["silhouette_change"]
        if delta is not None and delta < .04:
            warnings.append("Near-duplicate silhouette: verify intentional hold")
        if delta is not None and delta > .72:
            warnings.append("Large silhouette jump: inspect pivot and continuity")
        if i in hit_poses:
            warnings.append("Hit-timed pose; actual limb/weapon contact NOT verified")
        roles.append({"index": i, "role_guess": label, "confidence": "unverified",
                      "warnings": warnings, "scan": scan})
    return roles


def candidate(move: dict, roles: list[dict], style: str) -> dict:
    """Beat timing alternatives preserving source pose order and hit ownership."""
    factors = {
        "precision": (.70, 1.16, .85, 1.35),
        "rush": (.82, .62, .73, 1.42),
        "weight": (1.25, 1.30, .70, .70),
    }
    if style not in factors:
        raise ValueError(f"Unknown style: {style}")
    old = [int(p["ticks"]) for p in move["poses"]]
    total = int(move["duration_ticks"])
    if sum(old) != total or len(roles) != len(old) or total < 3*len(old):
        raise ValueError("Invalid source pose duration or role budget")
    weights = []
    for role in roles:
        label = role["role_guess"]
        contact, anticipation, transition, recovery = factors[style]
        weights.append({"candidate_contact": contact, "candidate_anticipation": anticipation,
                        "candidate_transition": transition, "candidate_recovery": recovery}[label])
    new = retime(old, weights, total, minimum=3)
    beats = []
    at = 0
    for i, duration in enumerate(new):
        beats.append({"pose_index": i, "start_tick": at,
                      "end_tick_exclusive": at+duration, "duration_ticks": duration,
                      "proposed_stage": roles[i]["role_guess"], "verified": False})
        at += duration
    hits = []
    for event in move["hit_events"]:
        original_tick = int(event["tick"])
        original_end = int(event.get("end_tick", original_tick))
        idx, _ = pose_for_tick(move["poses"], original_tick)
        new_tick = map_tick(old, new, original_tick)
        new_end = min(new_tick + max(0, original_end-original_tick),
                      sum(new[:idx+1])-1, total-1)
        hits.append({"event_id": event["id"], "source_tick": original_tick,
                     "proposed_tick": new_tick, "proposed_end_tick": new_end,
                     "pose_index": idx, "original_damage": event.get("damage"),
                     "contact_verified": False,
                     "effect_hint": event.get("effect", event.get("kind", "impact"))})
    return {
        "style": style, "sequence_id": move["sequence_id"],
        "status": "UNAPPROVED_AUTHORING_DRAFT", "duration_ticks": total,
        "source_pose_paths": [p["path"] for p in move["poses"]],
        "pose_ticks": new, "beats": beats, "hit_proposals": hits,
        "audio_directives": {"voice_policy": "opening_or_finisher_only",
                             "files_assigned": False, "impact_policy": "confirmed_hits_only"},
        "constraints": ["gameplay and damage unchanged", "pose order preserved",
                        "contact must be validated in Godot, both facings",
                        "movement, cues, cancels and target reactions NOT retimed"],
    }


def generate(move: dict, root: Path = ROOT) -> dict:
    if (move.get("category") != "normal"
            or len(move.get("poses", [])) < 3
            or not move.get("hit_events")):
        raise ValueError("Only authored normal attacks with pose/hit tracks supported")
    total = int(move["duration_ticks"])
    if any(int(h["tick"]) < 0 or int(h["tick"]) >= total for h in move["hit_events"]):
        raise ValueError("Hit outside source timeline")
    scans = scan_move(move, root)
    roles = stage_suggestions(move, scans)
    proposals = {style: candidate(move, roles, style) for style in STYLES}
    checksum = hashlib.sha256(json.dumps(move, sort_keys=True).encode()).hexdigest()
    return {"schema": 1, "source_sequence_id": move["sequence_id"],
            "source_sha256": checksum, "scope": "offline review only; not gameplay data",
            "pose_hypotheses": roles, "candidates": proposals}


def render_html(review: dict, out: Path) -> None:
    """Local-file pose gallery; path resolution assumes output remains under project."""
    try:
        relative = out.parent.resolve().relative_to(ROOT.resolve())
        prefix = "../" * len(relative.parts)
    except ValueError:
        prefix = ""
    title = html.escape(review["source_sequence_id"])
    pieces = [
        '<!doctype html><html lang="en"><meta charset="utf-8">',
        f"<title>Choreography Director · {title}</title>",
        '<style>body{background:#121825;color:#edf2fc;font:14px system-ui;'
        'margin:30px auto;max-width:1050px}.cols{display:grid;grid-template-columns:'
        'repeat(3,1fr);gap:12px}.card{border:1px solid #3f5166;border-radius:12px;'
        'padding:12px;background:#1c2636}.track{display:flex;height:24px}'
        '.track span{border-right:1px solid #aaa;background:#344966;position:relative}'
        '.track b{position:absolute;top:2px;left:0;color:#ffda6b;font:12px system-ui}'
        '.poses{display:flex;gap:10px;flex-wrap:wrap}.pose{border:1px solid #47566b;'
        'padding:8px}.pose img{width:100px;height:120px;object-fit:contain;'
        'image-rendering:pixelated}small{color:#c7d1df}.warn{color:#ffcb77}</style>',
        f"<h1>{title}</h1><p class=warn>UNAPPROVED: contact and action identity "
        "cannot be established by alpha silhouette features.</p><div class=cols>",
    ]
    for style, move in review["candidates"].items():
        pieces.append(f'<section class=card><h2>{html.escape(style.title())}</h2><div class=track>')
        for beat in move["beats"]:
            width = 100 * beat["duration_ticks"] / move["duration_ticks"]
            active = any(h["pose_index"] == beat["pose_index"] for h in move["hit_proposals"])
            pieces.append(f'<span title="{html.escape(beat["proposed_stage"])}" '
                          f'style="width:{width:.3f}%"><b>{"●" if active else ""}</b></span>')
        points = ", ".join(f'{html.escape(str(h["event_id"]))} @ {h["proposed_tick"]}'
                           for h in move["hit_proposals"])
        pieces.append(f"</div><p><small>Hit timing: {points}</small></p></section>")
    pieces.append("</div><h2>Source sprite pose gallery</h2><div class=poses>")
    for role in review["pose_hypotheses"]:
        scan = role["scan"]
        url = html.escape(prefix + scan["pose_path"].removeprefix("res://"), quote=True)
        pieces.append(f'<div class=pose><img loading=lazy src="{url}">'
                      f'<p>Pose {scan["index"]}: {html.escape(role["role_guess"])}</p>'
                      f'<small>Silhouette change: {scan["silhouette_change"]}</small>'
                      '<p class=warn>UNVERIFIED</p></div>')
    pieces.append("</div><small>No game timelines, hitbox geometry or damage were changed.</small></html>")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(pieces), encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--move", action="append", help="Sequence ID; repeatable")
    p.add_argument("--out", type=Path, default=ROOT / "docs/director_beats")
    args = p.parse_args()
    bank = {m["sequence_id"]: m for m in json.loads(MASTER.read_text())["moves"]}
    for name in args.move or ["chunli_neutral", "dante_neutral", "kosmos_arc"]:
        if name not in bank:
            p.error(f"Unknown sequence: {name}")
        proposal = generate(bank[name])
        folder = args.out / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "drafts.json").write_text(json.dumps(proposal, indent=2) + "\n")
        render_html(proposal, folder / "review.html")
        print(f"{name}: {len(proposal['pose_hypotheses'])} inspected poses; "
              f"{len(proposal['candidates'])} unapproved proposals → {folder}")


if __name__ == "__main__":
    main()
