#!/usr/bin/env python3
"""Contact Lab: source-pixel contact probes and synchronized review-only move drafts.

Samples the actual sprite alpha mask in Godot's local actor coordinates. Opaque
pixels overlapping the hit box are only a geometric proxy, never proof of a
correct limb/weapon contact or that the move connected with a moving target.
No shipping resources are written.
"""
from __future__ import annotations

import argparse
import copy
import html
import json
import math
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.choreography_director import map_tick, pose_for_tick
from tools.director_beat_composer import ROOT, generate

MASTER = ROOT / "moves" / "choreography.json"
PILOT_IDS = ("chunli_neutral", "dante_neutral", "kosmos_arc")
WINDOWS = ("chain_open", "chain_close", "cancel_open", "cancel_close")
STAGING_TIMES = ("approach_start", "approach_end", "commit_tick", "exit_start", "exit_end")
TIMED_FIELDS = ("tick", "start_tick", "end_tick")
ALPHA_MIN = 48


def point_map(old: list[int], new: list[int], tick: int) -> int:
    """Map timeline points; preserve end-exclusive duration boundaries."""
    length = sum(old)
    if not 0 <= tick <= length:
        raise ValueError(f"Source tick {tick} outside 0..{length}")
    return sum(new) if tick == length else map_tick(old, new, tick)


def synced_draft(move: dict, proposed_ticks: list[int]) -> dict:
    """Retime dependent tracks from one mapping, not just sprites and damage.

    Output remains an authoring draft, NEVER an automatically installed move.
    """
    old = [int(p["ticks"]) for p in move["poses"]]
    new = [int(v) for v in proposed_ticks]
    total = int(move["duration_ticks"])
    if len(old) != len(new) or any(n < 2 for n in new) or sum(old) != total or sum(new) != total:
        raise ValueError("Pose count, positive duration and original tick budget must agree")
    draft = copy.deepcopy(move)
    for p, duration in zip(draft["poses"], new):
        p["ticks"] = duration
    for original, event in zip(move["hit_events"], draft["hit_events"]):
        tick = int(original["tick"])
        end = int(original.get("end_tick", tick))
        if tick < 0 or end < tick or end >= total:
            raise ValueError(f"Invalid hit interval {tick}..{end}")
        original_index, _ = pose_for_tick(move["poses"], tick)
        mapped_tick = point_map(old, new, tick)
        if pose_for_tick(draft["poses"], mapped_tick)[0] != original_index:
            raise ValueError("Hit changed ownership to different pose")
        # Preserve the hit's source-pose association, including active-window end.
        original_end_index, _ = pose_for_tick(move["poses"], end)
        if original_end_index != original_index:
            raise ValueError("Cannot safely retime hit that spans multiple source poses")
        mapped_end = min(point_map(old, new, end), sum(new[:original_index + 1]) - 1)
        event["tick"], event["end_tick"] = mapped_tick, max(mapped_tick, mapped_end)
    for field in ("cues", "movement"):
        for record in draft.get(field, []):
            for key in TIMED_FIELDS:
                if key in record:
                    record[key] = point_map(old, new, int(record[key]))
    for key in WINDOWS:
        if key in draft:
            draft[key] = point_map(old, new, int(move[key]))
    for key in STAGING_TIMES:
        if key in draft.get("staging", {}):
            draft["staging"][key] = point_map(old, new, int(move["staging"][key]))
    # Any compressed staging interval must be rejected rather than silently
    # creating teleporting movement or a nonsensical cancel gate.
    stage = draft.get("staging", {})
    for start, end in (("approach_start", "approach_end"), ("exit_start", "exit_end")):
        if start in stage and end in stage and stage[start] >= stage[end]:
            raise ValueError(f"Staging collapsed: {start} >= {end}")
    for start, end in (("cancel_open", "cancel_close"), ("chain_open", "chain_close")):
        if start in draft and end in draft and draft[start] > draft[end]:
            raise ValueError(f"Window reversed: {start} > {end}")
    draft["_director_review"] = {
        "status": "UNAPPROVED; NOT FOR RUNTIME",
        "pose_ticks_before": old,
        "pose_ticks_after": new,
        "note": "Synchronized timing tracks only. Effects, hit geometry, and target motion remain physically unverified.",
    }
    return draft


def contact_probe(move: dict, event: dict, root: Path = ROOT,
                  sprite_scale: float = 1.7, facing: int = 1) -> dict:
    """Find closest opaque sprite pixel to the local melee hitbox.

    Mirrors exactly the *non-tilted* BattleActor transform for x; assumes no
    pose_offset/tilt/elevation, so final visual approval requires the Godot stage.
    """
    if facing not in (-1, 1) or sprite_scale <= 0:
        raise ValueError("Invalid facing or sprite scale")
    box = event.get("region")
    if not isinstance(box, list) or len(box) != 4 or box[2] <= 0 or box[3] <= 0:
        raise ValueError("Only positive-area melee hit regions are supported")
    tick = int(event["tick"])
    pose_index, _ = pose_for_tick(move["poses"], tick)
    pose = move["poses"][pose_index]
    source = str(pose["path"])
    if not source.startswith("res://"):
        raise ValueError("Expected local Godot asset path")
    from PIL import Image
    png = root / source[6:]
    with Image.open(png) as im:
        alpha = im.convert("RGBA").getchannel("A")
        width, height = alpha.size
        pixels = alpha.tobytes()
    anchor = pose.get("anchor", [])
    if len(anchor) != 2:
        raise ValueError("Missing source-pixel pose anchor")
    native = int(pose.get("native_facing", 1))
    if native not in (-1, 1):
        raise ValueError("Invalid native pose facing")
    off = pose.get("offset", [0, 0])
    x0, y0, rw, rh = [float(v) for v in box]
    if facing < 0:
        x0 = -x0 - rw
    x1, y1 = x0 + rw, y0 + rh
    mid_x, mid_y = x0 + rw / 2, y0 + rh / 2
    count = 0
    best = None
    nearest_distance2 = float("inf")
    best_center2 = float("inf")
    for index, alpha_value in enumerate(pixels):
        if alpha_value < ALPHA_MIN:
            continue
        px, py = index % width, index // width
        local_x = (float(px) - float(anchor[0])) * sprite_scale + float(off[0])
        local_x *= facing * native
        local_y = (float(py) - float(anchor[1])) * sprite_scale + float(off[1])
        dx = max(x0 - local_x, 0.0, local_x - x1)
        dy = max(y0 - local_y, 0.0, local_y - y1)
        dist2 = dx * dx + dy * dy
        if dist2 == 0.0:
            count += 1
        center2 = (local_x - mid_x) ** 2 + (local_y - mid_y) ** 2
        if dist2 < nearest_distance2 or (dist2 == nearest_distance2 and center2 < best_center2):
            nearest_distance2, best_center2 = dist2, center2
            best = ([px, py], [round(local_x, 2), round(local_y, 2)])
    if best is None:
        raise ValueError(f"Sprite contains no visible pixels: {source}")
    distance = round(math.sqrt(nearest_distance2), 2)
    if count:
        proxy = "visible_alpha_overlaps_attack_region"
    elif distance <= 12:
        proxy = "near_attack_region"
    else:
        proxy = "far_from_attack_region"
    return {
        "event_id": event["id"], "source_pose_index": pose_index, "source_pose_path": source,
        "source_tick": tick, "facing": facing, "sprite_scale": sprite_scale,
        "attack_region_actor_local": [round(v, 2) for v in [x0, y0, rw, rh]],
        "opaque_pixel_count_in_region": count, "nearest_distance_actor_units": distance,
        "suggested_source_pixel": best[0], "suggested_actor_local_pixel": best[1],
        "geometry_proxy": proxy, "semantic_contact": "UNVERIFIED",
        "requires_review": "Limb/weapon identity, target motion, sprite tilt and live alignment must be inspected.",
    }


def render_overlay(move: dict, event: dict, probe: dict, out: Path, root: Path = ROOT) -> None:
    """Visual contact proofing: source-pixel sprite and exact actor-local hitbox."""
    from PIL import Image, ImageDraw
    pose = move["poses"][probe["source_pose_index"]]
    with Image.open(root / pose["path"][6:]) as im:
        sprite = im.convert("RGBA")
    scale = probe["sprite_scale"]
    w, h = sprite.size
    sprite = sprite.resize((round(w * scale), round(h * scale)), Image.Resampling.NEAREST)
    native = int(pose.get("native_facing", 1))
    if probe["facing"] * native < 0:
        sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    canvas = Image.new("RGBA", (950, 650), (20, 29, 43, 255))
    ox, oy = 485, 450
    anchor = pose["anchor"]
    offset = pose.get("offset", [0, 0])
    if probe["facing"] * native >= 0:
        left = ox - round(float(anchor[0]) * scale) + round(float(offset[0]))
    else:
        left = ox - round((w - 1 - float(anchor[0])) * scale) - round(float(offset[0]))
    top = oy - round(float(anchor[1]) * scale) + round(float(offset[1]))
    canvas.alpha_composite(sprite, (left, top))
    draw = ImageDraw.Draw(canvas)
    box = probe["attack_region_actor_local"]
    x, y, bw, bh = box
    draw.rectangle((ox+x, oy+y, ox+x+bw, oy+y+bh), outline=(255, 204, 85, 255), width=3)
    point_x, point_y = probe["suggested_actor_local_pixel"]
    draw.ellipse((ox+point_x-6, oy+point_y-6, ox+point_x+6, oy+point_y+6),
                 fill=(255, 80, 122, 240), outline=(255, 255, 255, 255), width=2)
    draw.line((ox-12, oy, ox+12, oy), fill=(95, 205, 240, 255), width=2)
    draw.line((ox, oy-12, ox, oy+12), fill=(95, 205, 240, 255), width=2)
    draw.text((20, 18), f"{move['sequence_id']} | {event['id']} | facing {probe['facing']:+d}",
              fill=(239, 247, 255, 255))
    draw.text((20, 45), f"{probe['geometry_proxy']} | visible pixels in hit region: {probe['opaque_pixel_count_in_region']}",
              fill=(255, 219, 151, 255))
    draw.text((20, 74), "UNVERIFIED geometry only: this is not evidence of an actual combat hit",
              fill=(255, 161, 176, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out)


def create_review(move: dict, root: Path = ROOT) -> dict:
    bank = generate(move, root=root)
    probes = []
    for event in move["hit_events"]:
        # Mirroring regression: sampling actor facing -1 must behave as +1.
        plus = contact_probe(move, event, root=root, facing=1)
        minus = contact_probe(move, event, root=root, facing=-1)
        if plus["opaque_pixel_count_in_region"] != minus["opaque_pixel_count_in_region"]:
            raise ValueError(f"Mirroring geometry diverged for {event['id']}")
        probes.append({"normal_facing": plus, "mirrored_facing": minus})
    compiled = {}
    for style, original_proposal in bank["candidates"].items():
        draft = synced_draft(move, original_proposal["pose_ticks"])
        source_hits = [h["id"] for h in move["hit_events"]]
        if [h["id"] for h in draft["hit_events"]] != source_hits:
            raise ValueError("Hit IDs changed")
        compiled[style] = {"draft": draft, "status": "UNAPPROVED", "visual_contact_verified": False}
    return {
        "schema_version": 1, "move": move["sequence_id"],
        "source_sha256": bank["source_sha256"], "contact_probes": probes,
        "pose_hypotheses": bank["pose_hypotheses"], "candidates": compiled,
        "release_gate": "Requires manual pose semantics and in-engine both-facing contact review",
        "not_validated": ["moving/airborne targets", "real target hurtbox", "camera/tilt",
                          "sprite details and weapon identity", "sound identity", "juggle/cancel feel"],
    }


def emit_review(move: dict, target: Path, root: Path = ROOT) -> dict:
    output = create_review(move, root=root)
    target.mkdir(parents=True, exist_ok=True)
    (target / "contact_review.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    cards = []
    for i, (event, pair) in enumerate(zip(move["hit_events"], output["contact_probes"])):
        for key, facing in (("normal_facing", 1), ("mirrored_facing", -1)):
            image = f"contact_{i:02d}_{'right' if facing == 1 else 'left'}.png"
            render_overlay(move, event, pair[key], target / image, root=root)
            cards.append(f'<div class="card"><img src="{html.escape(image)}" alt="hitbox sprite review">'
                         f'<p>{html.escape(event["id"])} — facing {facing:+d} '
                         f'<b>{pair[key]["opaque_pixel_count_in_region"]} opaque pixels in box</b></p></div>')
    studies = []
    for style, data in output["candidates"].items():
        draft = data["draft"]
        hits = ", ".join(f'{html.escape(x["id"])} @ {x["tick"]}'
                         for x in draft["hit_events"])
        studies.append(f'<tr><td>{html.escape(style)}</td><td>{html.escape(str([p["ticks"] for p in draft["poses"]]))}</td>'
                       f'<td>{hits}</td><td>{draft.get("cancel_open")}–{draft.get("cancel_close")}</td></tr>')
    page = ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<title>Director contact review</title><style>body{background:#101623;color:#edf1f8;'
            'font:14px system-ui;margin:30px auto;max-width:1100px}h1{font-size:25px}'
            '.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px}'
            '.card{background:#1c293a;border-radius:9px;padding:10px}.card img{max-width:100%}'
            'table{border-collapse:collapse;width:100%}td,th{padding:9px;border:1px solid #47566b;'
            'text-align:left}p{line-height:1.5}</style>'
            f'<h1>{html.escape(move["sequence_id"])} · Contact Lab</h1>'
            '<p><strong>UNAPPROVED.</strong> Gold = attack box; pink = suggested sprite pixel. '
            'Pixel overlap is only a geometric check, not proof of credible striking animation.</p>'
            '<div class="cards">' + "".join(cards) + '</div>'
            '<h2>Synchronized proposed tracks (NOT installed)</h2>'
            '<table><thead><tr><th>Style</th><th>Pose durations</th><th>Hit events</th>'
            '<th>Cancel window</th></tr></thead><tbody>' + "".join(studies) + '</tbody></table>'
            '<p>See contact_review.json for source identity, staging, movement, cue and hit tracks. '
            'Approval requires actual Godot visual/contact tests.</p></html>')
    (target / "review.html").write_text(page, encoding="utf-8")
    return output


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--move", action="append", help="Sequence id; may be repeated")
    p.add_argument("--out", type=Path, default=ROOT / "docs/director_contacts")
    args = p.parse_args()
    moves = {m["sequence_id"]: m for m in json.loads(MASTER.read_text())["moves"]}
    for name in args.move or PILOT_IDS:
        if name not in moves:
            p.error(f"Unknown move: {name}")
        result = emit_review(moves[name], args.out / name)
        counts = [x["normal_facing"]["opaque_pixel_count_in_region"]
                  for x in result["contact_probes"]]
        print(f"{name}: {len(counts)} hit events; opaque pixel overlap {counts}; "
              "3 synchronized, unapproved proposals")


if __name__ == "__main__":
    main()
