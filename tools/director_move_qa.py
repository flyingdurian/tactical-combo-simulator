#!/usr/bin/env python3
"""Director normal-attack quality contract (authoring validation).

New normals: 120..300 ticks at Godot's 60Hz. Similarity is measured from
ordered pose paths, not mere shared idle sprites. Legacy short moves are
reported as migration debt, not silently retimed or rejected.
"""
from __future__ import annotations
from collections import Counter
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MIN_NORMAL_TICKS, MAX_NORMAL_TICKS = 120, 300


def read_tres(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    result = {}
    for key in ("sequence_id", "character", "category", "duration_ticks", "purpose"):
        found = re.search(rf"^{key} = (.+)$", text, re.M)
        if not found:
            raise ValueError(f"Missing {key} in {path}")
        result[key] = json.loads(found.group(1))
    for key in ("poses", "hit_events"):
        found = re.search(rf"^{key} = Array\[Dictionary\]\((.+)\)$", text, re.M)
        if not found:
            raise ValueError(f"Missing {key} in {path}")
        result[key] = json.loads(found.group(1))
    return result


def pose_paths(move: dict) -> list[str]:
    return [p["path"] for p in move["poses"]]


def longest_common_run(a: list[str], b: list[str]) -> int:
    """Longest contiguous identical pose order, unlike shared individual sprites."""
    last = [0] * (len(b) + 1)
    best = 0
    for a_item in a:
        current = [0] * (len(b) + 1)
        for j, b_item in enumerate(b, 1):
            if a_item == b_item:
                current[j] = last[j-1] + 1
                best = max(best, current[j])
        last = current
    return best


def hit_pose_paths(move: dict) -> list[str]:
    poses = move.get("poses", [])
    events = move.get("hit_events", [])
    end_points = []
    total = 0
    for pose in poses:
        total += int(pose["ticks"])
        end_points.append(total)
    result = []
    for event in events:
        tick = int(event["tick"])
        try:
            index = next(i for i, end in enumerate(end_points) if tick < end)
        except StopIteration as exc:
            raise ValueError("Hit outside pose track") from exc
        if tick < 0:
            raise ValueError("Negative hit tick")
        result.append(poses[index]["path"])
    return result


def assess_new_normal(move: dict, peers: list[dict]) -> dict:
    errors = []
    warnings = []
    ticks = int(move["duration_ticks"])
    normal = move.get("category") == "normal" and move.get("role", "main") == "main"
    if not normal:
        errors.append("Not a playable normal attack")
    if not MIN_NORMAL_TICKS <= ticks <= MAX_NORMAL_TICKS:
        errors.append(f"Normal must be 2–5 seconds / {MIN_NORMAL_TICKS}–{MAX_NORMAL_TICKS} ticks; got {ticks}")
    poses = pose_paths(move)
    if len(poses) < 4 or len(set(poses)) < 4:
        errors.append("Too few distinct source poses")
    if sum(int(p["ticks"]) for p in move["poses"]) != ticks:
        errors.append("Pose durations do not sum to move duration")
    if any(int(p["ticks"]) <= 0 for p in move["poses"]):
        errors.append("Nonpositive pose duration")
    events = move["hit_events"]
    times = [int(e["tick"]) for e in events]
    if not times or any(t < 0 or t >= ticks for t in times) or sorted(times) != times:
        errors.append("Hit events invalid or not chronological")
    if len({e["id"] for e in events}) != len(events):
        errors.append("Duplicate hit event ID")
    own_hit_poses = hit_pose_paths(move)
    if not own_hit_poses:
        errors.append("Normal has no contact proposals")
    # An identical multi-frame attack phrase is qualitatively different
    # from reusing one idle pose. Both long snippets and complete hit
    # motif duplication should block auto-promotion.
    for peer in peers:
        if peer.get("character") != move.get("character"):
            continue
        if peer.get("category") != "normal" or peer.get("sequence_id") == move.get("sequence_id"):
            continue
        peer_paths = pose_paths(peer)
        run = longest_common_run(poses, peer_paths)
        if run >= 7 and run >= len(poses) * 0.45:
            errors.append(f"Near-duplicate visual phrase: {peer['sequence_id']} ({run} contiguous frames)")
        elif run >= 4:
            warnings.append(f"Review source-pose reuse vs {peer['sequence_id']}: {run} contiguous frames")
        peer_hit = hit_pose_paths(peer)
        if len(own_hit_poses) >= 2 and own_hit_poses == peer_hit:
            errors.append(f"Identical striking-pose motif to {peer['sequence_id']}")
    # A repeated 3-pose cycle within a single move often indicates
    # an auto-generated filler loop. Flag for creative review.
    triplets = Counter(tuple(poses[i:i+3]) for i in range(len(poses)-2))
    if any(count >= 3 for count in triplets.values()):
        warnings.append("Repeated 3-pose phrase within the same move")
    hit_gaps = [b-a for a,b in zip(times,times[1:])]
    if hit_gaps and len(set(hit_gaps)) == 1 and len(hit_gaps) >= 4:
        warnings.append("Machine-gun hit cadence: all gaps identical")
    if not errors and warnings:
        state = "valid_with_creative_review"
    else:
        state = "invalid" if errors else "structurally_valid"
    return {"sequence_id": move.get("sequence_id"), "duration_ticks": ticks,
            "duration_seconds": round(ticks/60, 3), "hit_count": len(events),
            "distinct_pose_count": len(set(poses)), "status": state,
            "errors": errors, "warnings": warnings,
            "visual_contact_verdict": "UNVERIFIED — requires both-facing Godot playback"}


def legacy_audit(moves: list[dict]) -> dict:
    rows = []
    for move in moves:
        if move.get("category") != "normal" or move.get("role") != "main":
            continue
        ticks = int(move["duration_ticks"])
        if not MIN_NORMAL_TICKS <= ticks <= MAX_NORMAL_TICKS:
            rows.append({"sequence_id": move["sequence_id"], "character": move["character"],
                         "current_ticks": ticks, "target_ticks": [MIN_NORMAL_TICKS, MAX_NORMAL_TICKS]})
    return {"legacy_normals_outside_duration_target": rows,
            "note": "Migration debt only: never automatically stretch shipped combat."}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--preview", type=Path, default=ROOT / "moves/director_drafts/chunli_neutral_b_preview.tres")
    p.add_argument("--out", type=Path, default=Path("/tmp/director-normal-quality.json"))
    args = p.parse_args()
    moves = json.loads((ROOT / "moves/choreography.json").read_text())["moves"]
    preview = read_tres(args.preview)
    report = {"contract": {"regular_attack_seconds": [2, 5], "normal_ticks": [120, 300],
                            "roster_normals": [5, 6], "supers": 2, "ultimates": 1},
              "new_preview": assess_new_normal(preview, moves),
              "legacy_debt": legacy_audit(moves)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Normal QA: {report['new_preview']['status']}, "
          f"{len(report['new_preview']['warnings'])} creative warnings; "
          f"{len(report['legacy_debt']['legacy_normals_outside_duration_target'])} legacy duration migrations")
    if report["new_preview"]["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
