#!/usr/bin/env python3
"""16-fighter sprite vocabulary and repertoire ownership — review-only.

This is an evidence inventory, NOT a pose-recognition model. Alpha geometry
cannot prove kick/sword/weapon identity or target contact. Every inferred stage
and every proposed new role stays unapproved until a named review record
supplies an inspected source frame and a valid local contact anchor.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import html
import json
from pathlib import Path

from tools.director_repertoire import (
    ROOT, BLUEPRINT, SOURCE, ALL_SLOTS, MAIN_SLOTS,
    common_run, contact_pose_paths, role_assignment,
)

REVIEW_ROLES = frozenset({
    "anticipation", "approach", "strike", "follow_through",
    "recovery", "guard", "airborne", "hold", "effect_only",
})
UNVERIFIED = "UNREVIEWED_SOURCE_PIXEL"
SCHEMA_VERSION = 1


def _source_pose(move: dict, tick: int) -> int:
    if tick < 0:
        raise ValueError("Negative event tick")
    cursor = 0
    for i, p in enumerate(move.get("poses", [])):
        cursor += int(p["ticks"])
        if tick < cursor:
            return i
    raise ValueError("Hit event outside authored poses: " + move["sequence_id"])


def _bounds(path: str, root: Path, cache: dict) -> dict:
    if path in cache:
        return cache[path]
    if not path.startswith("res://"):
        raise ValueError(f"Invalid local path: {path}")
    filename = (root / path[6:]).resolve()
    if not filename.is_relative_to(root.resolve()) or not filename.is_file():
        raise FileNotFoundError(path)
    try:
        from PIL import Image
    except ImportError as e:
        raise RuntimeError("Pillow is required for source-alpha proofing") from e
    with Image.open(filename) as im:
        im.load()
        alpha = im.convert("RGBA").getchannel("A")
        bbox = alpha.getbbox()
        if bbox is None:
            raise ValueError("Empty sprite " + path)
        width, height = im.size
        # This is a geometry hint only. A lowest pixel is NOT a verified foot.
        mask = alpha.tobytes()
        nontransparent = sum(v >= 32 for v in mask)
    out = {
        "canvas": [width, height],
        "alpha_bbox": list(bbox),
        "visible_alpha_ratio": round(nontransparent / max(1, width * height), 4),
        "geometry_confidence": "PIXEL_MEASURED",
        "semantic_confidence": UNVERIFIED,
    }
    cache[path] = out
    return out


def _frame_class(move: dict, pose_index: int) -> str:
    event_indices = [_source_pose(move, int(e["tick"]))
                     for e in move.get("hit_events", [])]
    if not event_indices:
        return "unknown_no_hit_provenance"
    if pose_index in event_indices:
        return "hit_timed_not_contact_verified"
    if pose_index < min(event_indices):
        return "pre_hit_timing_only"
    if pose_index > max(event_indices):
        return "post_hit_timing_only"
    return "inter_hit_timing_only"


def collect_vocabulary(source: dict, blueprint: dict,
                       root: Path = ROOT, reviews: dict | None = None) -> dict:
    roster = sorted(name for name in blueprint["characters"])
    actual = sorted({m["character"] for m in source["moves"]
                     if m["character"] != "placeholder_cpu"})
    if roster != actual or len(roster) != 16:
        raise ValueError("Source and blueprint must contain the same 16 fighters")
    reviews = reviews or {"schema_version": SCHEMA_VERSION, "characters": {}}
    if reviews.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported review schema")
    unknown_review_names = set(reviews.get("characters", {})) - set(roster)
    if unknown_review_names:
        raise ValueError(f"Unknown reviewed fighter(s): {sorted(unknown_review_names)}")
    geometry_cache = {}
    results = {}
    for fighter in roster:
        main = [m for m in source["moves"]
                if m["character"] == fighter and m.get("role") == "main"]
        poses: dict[str, dict] = {}
        by_slot = {slot: [] for slot in ALL_SLOTS}
        sources = {}
        for move in main:
            slot = role_assignment(move)
            if slot in by_slot:
                by_slot[slot].append(move["sequence_id"])
            all_hit_indices = [_source_pose(move, int(e["tick"]))
                               for e in move.get("hit_events", [])]
            contact_paths = contact_pose_paths(move)
            sources[move["sequence_id"]] = {
                "role_slot_inferred": slot,
                "category": move["category"],
                "duration_ticks": int(move["duration_ticks"]),
                "source_pose_count": len(move["poses"]),
                "hit_timed_pose_paths": contact_paths,
                "hit_motif_hash": sha256("\n".join(contact_paths).encode()).hexdigest(),
                "semantics_verified": False,
            }
            for i, p in enumerate(move["poses"]):
                path = p["path"]
                if path not in poses:
                    poses[path] = {
                        "path": path,
                        "pixels": _bounds(path, root, geometry_cache),
                        "source_uses": [],
                        "hit_event_refs": [],
                        "distinct_source_move_count": 0,
                        "role_inference": [],
                        "semantic_review": {
                            "status": "UNREVIEWED", "pose_role": None,
                            "contact_anchor_source_px": None,
                            "reviewer": None, "evidence_note": None,
                        },
                    }
                record = poses[path]
                record["source_uses"].append({
                    "move": move["sequence_id"], "pose_index": i,
                    "stage_guess": _frame_class(move, i),
                    "pose_ticks": int(p["ticks"]),
                    "native_facing": p.get("native_facing"),
                    "source_anchor_px": p.get("anchor"),
                    "pose_offset": p.get("offset", [0, 0]),
                    "role_slot_inferred": slot,
                })
                if slot and slot not in record["role_inference"]:
                    record["role_inference"].append(slot)
                for event in move.get("hit_events", []):
                    if _source_pose(move, int(event["tick"])) != i:
                        continue
                    record["hit_event_refs"].append({
                        "move": move["sequence_id"], "event_id": event["id"],
                        "tick": int(event["tick"]),
                        "region_actor_local": event.get("region"),
                        "reaction": event.get("reaction"),
                        "launch": event.get("launch", 0),
                        "knockback": event.get("knockback", 0),
                        "evidence": "EXISTING_EVENT_TIMING_NOT_VISUAL_CONTACT",
                    })
        manual_reviews = reviews.get("characters", {}).get(fighter, {})
        if not isinstance(manual_reviews, dict):
            raise ValueError("Artist reviews must be keyed by frame path")
        if set(manual_reviews) - set(poses):
            raise ValueError(f"{fighter} review refers to absent/unused frames: "
                             f"{sorted(set(manual_reviews)-set(poses))[:3]}")
        for path, entry in poses.items():
            entry["distinct_source_move_count"] = len(
                {x["move"] for x in entry["source_uses"]})
            entry["role_inference"].sort()
            if path in manual_reviews:
                entry["semantic_review"] = validate_review(
                    path, manual_reviews[path], entry["pixels"])
        by_slot_signatures = {}
        for slot, move_ids in by_slot.items():
            hitpaths = [p for move_id in move_ids
                        for p in sources[move_id]["hit_timed_pose_paths"]]
            certified = [p for p in hitpaths if
                         poses[p]["semantic_review"]["status"] == "VERIFIED_BY_REVIEWER"
                         and poses[p]["semantic_review"]["pose_role"] == "strike"]
            by_slot_signatures[slot] = {
                "design_intent": blueprint["characters"][fighter]["slots"][slot]["unique_identity"],
                "existing_move_ids": move_ids,
                "hit_timed_source_paths": hitpaths,
                "reviewed_striking_source_paths": sorted(set(certified)),
                "signature_reserved": len(set(certified)) >= 2,
                "release_status": "REVIEW_NEEDED",
            }
        overlap = []
        for i, (a, move_a) in enumerate(sources.items()):
            for b, move_b in list(sources.items())[i+1:]:
                a_paths = move_a["hit_timed_pose_paths"]
                b_paths = move_b["hit_timed_pose_paths"]
                shared = sorted(set(a_paths) & set(b_paths))
                if not shared:
                    continue
                overlap.append({
                    "moves": [a, b],
                    "shared_hit_timed_poses": shared,
                    "same_exact_hit_motif": len(a_paths) > 1 and a_paths == b_paths,
                    "risk": "REQUIRES_VISUAL_REVIEW_NOT_PROOF_OF_REPETITION",
                })
        results[fighter] = {
            "identity_intent": blueprint["characters"][fighter]["archetype_intent"],
            "pose_count": len(poses),
            "hit_timed_pose_count": sum(bool(p["hit_event_refs"]) for p in poses.values()),
            "reviewed_pose_count": sum(p["semantic_review"]["status"] == "VERIFIED_BY_REVIEWER"
                                       for p in poses.values()),
            "source_moves": sources,
            "slots": by_slot_signatures,
            "poses": poses,
            "cross_move_hit_pose_overlap": overlap,
            "readiness": "PREPRODUCTION_REVIEW_REQUIRED",
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "source_sha256": sha256(json.dumps(source, sort_keys=True).encode()).hexdigest(),
        "blueprint_sha256": sha256(json.dumps(blueprint, sort_keys=True).encode()).hexdigest(),
        "purpose": "SOURCE_POSE_SEMANTIC_REVIEW_NOT_PLAYABLE_MOVES",
        "all_repertoire_roles_reviewed": False,
        "characters": results,
        "summary": {
            "fighters": len(results),
            "unique_source_pose_paths": sum(row["pose_count"] for row in results.values()),
            "hit_timed_pose_paths": sum(row["hit_timed_pose_count"] for row in results.values()),
            "source_move_slots": sum(len(row["source_moves"]) for row in results.values()),
            "human_verified_pose_records": sum(row["reviewed_pose_count"] for row in results.values()),
            "cross_move_hit_pose_conflicts_to_review": sum(
                len(row["cross_move_hit_pose_overlap"]) for row in results.values()),
        },
    }


def validate_review(path: str, review: dict, geometry: dict) -> dict:
    if not isinstance(review, dict):
        raise ValueError("Bad review record: " + path)
    role = review.get("pose_role")
    if role not in REVIEW_ROLES:
        raise ValueError("Unknown role label for " + path)
    anchor = review.get("contact_anchor_source_px")
    if anchor is not None:
        if not isinstance(anchor, list) or len(anchor) != 2 or any(
                not isinstance(v, (int, float)) or isinstance(v, bool) for v in anchor):
            raise ValueError("Bad source-pixel contact anchor: " + path)
        w, h = geometry["canvas"]
        if not (0 <= anchor[0] < w and 0 <= anchor[1] < h):
            raise ValueError("Out-of-image contact anchor: " + path)
    status = review.get("status")
    if status != "VERIFIED_BY_REVIEWER":
        raise ValueError("Only explicit reviewer-approved records may be imported")
    if not isinstance(review.get("reviewer"), str) or len(review["reviewer"].strip()) < 2:
        raise ValueError("Reviewer identity missing for " + path)
    if not isinstance(review.get("evidence_note"), str) or len(review["evidence_note"].strip()) < 8:
        raise ValueError("Reviewer evidence note missing for " + path)
    if role == "strike" and anchor is None:
        raise ValueError("Strike requires inspected pixel contact anchor: " + path)
    return {
        "status": "VERIFIED_BY_REVIEWER",
        "pose_role": role,
        "contact_anchor_source_px": anchor,
        "reviewer": review["reviewer"].strip(),
        "evidence_note": review["evidence_note"].strip(),
    }


def compose_guard(candidate: dict, roster: dict, verified_only: bool = True) -> dict:
    """Reject near-copies before sending the candidate to a gameplay compiler."""
    fighter = candidate.get("character")
    if fighter not in roster["characters"]:
        raise ValueError("Unknown roster fighter")
    row = roster["characters"][fighter]
    paths = [p["path"] for p in candidate.get("poses", [])]
    if len(paths) < 4:
        return {"allowed": False, "reasons": ["Insufficient sprite phrase"], "status":"BLOCKED"}
    recognized = row["poses"]
    errors, warnings = [], []
    unknown = sorted(set(paths) - set(recognized))
    if unknown:
        errors.append(f"Pose files not in reviewed source registry: {len(unknown)}")
    unreviewed = [p for p in paths if p in recognized and
                  recognized[p]["semantic_review"]["status"] != "VERIFIED_BY_REVIEWER"]
    if verified_only and unreviewed:
        errors.append(f"{len(set(unreviewed))} source poses lack explicit semantic review")
    for move_id, source in row["source_moves"].items():
        other = next((use["move"] for pose in row["poses"].values()
                      for use in pose["source_uses"] if use["move"] == move_id), None)
        if not other:
            continue
        other_poses = sorted(
            ((use["pose_index"], pose["path"]) for pose in row["poses"].values()
             for use in pose["source_uses"] if use["move"] == move_id),
            key=lambda v: v[0])
        run = common_run(paths, [p for _,p in other_poses])
        if run >= 7 and run >= .45 * len(paths):
            errors.append(f"Near-identical multi-pose run to {move_id} ({run} frames)")
        elif run >= 4:
            warnings.append(f"Source phrase reuse with {move_id} ({run} frames)")
    return {
        "allowed": not errors,
        "status": "REVIEW_ONLY" if not errors else "BLOCKED",
        "reasons": errors,
        "warnings": warnings,
        "note": "Mechanical and artistic approval are independent gates.",
    }


def render_html(roster: dict) -> str:
    blocks = []
    for fighter, row in sorted(roster["characters"].items()):
        slots = "".join(
            f"<tr><td>{html.escape(slot)}</td><td>{html.escape(s['design_intent'])}</td>"
            f"<td>{html.escape(', '.join(s['existing_move_ids']) or 'UNASSIGNED')}</td>"
            f"<td>{len(s['reviewed_striking_source_paths'])} / source {len(s['hit_timed_source_paths'])}</td></tr>"
            for slot, s in row["slots"].items())
        hit_records = [p for p in row["poses"].values() if p["hit_event_refs"]]
        examples = "".join(
            f"<li><code>{html.escape(p['path'].split('/')[-1])}</code> — "
            f"{len(p['hit_event_refs'])} authored hit-timed event(s), "
            f"semantics {html.escape(p['semantic_review']['status'])}</li>"
            for p in hit_records[:12])
        blocks.append(
            "<details><summary>" + html.escape(fighter) + f" — {row['pose_count']} source poses, "
            f"{len(row['cross_move_hit_pose_overlap'])} reuse flags</summary>"
            "<p>All move labels inferred from authored timings/IDs; no strike semantics automatically verified.</p>"
            "<table><thead><tr><th>Role</th><th>Intended identity</th><th>Current source</th><th>Verified strikes</th></tr></thead>"
            f"<tbody>{slots}</tbody></table><h3>Hit-timed source frame examples</h3><ul>{examples}</ul></details>")
    return ("""<!doctype html><html lang="en"><meta charset="utf-8">
<title>Director — 16-fighter pose vocabulary</title>
<style>body{font:15px system-ui;background:#121b28;color:#eaf0fa;max-width:1120px;margin:30px auto;padding:12px}
details{border:1px solid #425a70;border-radius:10px;padding:14px;margin:10px 0}summary{font-size:19px;cursor:pointer}
table{width:100%;border-collapse:collapse}td,th{padding:7px;text-align:left;border:1px solid #41566e}
.warn{color:#ffcf80}</style><h1>16-fighter pose evidence & identity</h1>
<p class="warn">ARTIST REVIEW REQUIRED — source pixels and hit-event timestamps do not prove attack identity,
weapon anchors or target contact. This report cannot approve new playable moves.</p>"""
            + "\n".join(blocks) + "</html>")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=ROOT / "docs/director_vocabulary")
    p.add_argument("--reviews", type=Path, default=None)
    args = p.parse_args()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    reviews = json.loads(args.reviews.read_text(encoding="utf-8")) if args.reviews else None
    report = collect_vocabulary(source, blueprint, ROOT, reviews)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "pose_vocabulary.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.out / "review.html").write_text(render_html(report))
    print("Pose Vocabulary: " + json.dumps(report["summary"], sort_keys=True))
    print("Review gate: %d verified poses / all fighter moves remain UNAPPROVED" %
          report["summary"]["human_verified_pose_records"])


if __name__ == "__main__":
    main()
