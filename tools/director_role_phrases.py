#!/usr/bin/env python3
"""Director role contract and source-pose phrase assembly (authoring-only).

Never installs or alters Godot moves. Mechanic classification is provisional;
sprite content is actual local PNGs, but visible action and contact aren't proven.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from PIL import Image
from tools.choreography_director import pose_for_tick

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "moves" / "choreography.json"
ROLES = ("neutral_combo", "juggle", "launcher", "wall_carry", "finisher")
REQUIRED = {"neutral_combo": 2, "juggle": 1, "launcher": 1, "wall_carry": 1}
MAX_NORMALS = 6
STYLES = ("precision", "rush", "finisher")


def load_moves(path: Path = MASTER) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["moves"]


def classify(move: dict) -> str | None:
    if move.get("role") != "main" or move.get("category") != "normal":
        return None
    suffix = move["sequence_id"].split("_")[-1]
    if suffix in ("neutral", "arc"):
        return "neutral_combo"
    if suffix in ("left", "barrage"):
        return "juggle"
    if suffix == "up":
        return "launcher"
    if suffix == "right":
        return "wall_carry"
    if suffix == "down":
        return "finisher"
    return None


def evidence(move: dict, role: str) -> list[str]:
    events = move.get("hit_events", [])
    if not events:
        return ["No authored hit events"]
    flags = []
    if role == "launcher" and not any(float(h.get("launch", 0)) >= 150 for h in events):
        flags.append("Launcher label lacks a >=150 launch event")
    if role == "juggle" and not any(
            h.get("reaction") in ("sustain", "rescue") or 0 < float(h.get("launch", 0)) < 150
            for h in events):
        flags.append("Juggle label lacks a sustain/rescue or limited-lift event")
    if role == "wall_carry":
        if not any(float(h.get("knockback", 0)) > 0
                   or "wall" in str(h.get("reaction", "")).lower() for h in events):
            flags.append("Wall carry is named but has no explicit positive knockback/wall reaction; runtime wall interaction unverified")
    if role == "finisher" and not any(h.get("reaction") == "finish" for h in events):
        flags.append("Finisher label lacks a finish reaction")
    return flags


def roster_audit(moves: list[dict]) -> dict:
    roster = {}
    for move in moves:
        character = move.get("character")
        if not character or character == "placeholder_cpu":
            continue
        roster.setdefault(character, {"role_moves": {r: [] for r in ROLES}, "supers": [],
                                      "ultimates": [], "assist_moves": [], "unclassified": [],
                                      "mechanic_warnings": []})
        row = roster[character]
        if move.get("role") == "assist":
            row["assist_moves"].append(move["sequence_id"])
            continue
        if move.get("role") != "main":
            continue
        cat = move.get("category")
        if cat == "special":
            row["supers"].append(move["sequence_id"])
        elif cat == "ultimate":
            row["ultimates"].append(move["sequence_id"])
        elif cat == "normal":
            role = classify(move)
            if role:
                row["role_moves"][role].append(move["sequence_id"])
                row["mechanic_warnings"].extend(
                    {"move": move["sequence_id"], "issue": flag}
                    for flag in evidence(move, role))
            else:
                row["unclassified"].append(move["sequence_id"])
    for char, row in roster.items():
        row["normal_count"] = sum(len(v) for v in row["role_moves"].values()) + len(row["unclassified"])
        row["missing_roles"] = {r: max(0, target - len(row["role_moves"][r]))
                                for r, target in REQUIRED.items()
                                if len(row["role_moves"][r]) < target}
        row["missing_supers"] = max(0, 2 - len(row["supers"]))
        row["missing_ultimates"] = max(0, 1 - len(row["ultimates"]))
        row["extra_normals"] = max(0, row["normal_count"] - MAX_NORMALS)
        row["has_required_content"] = (
            not row["missing_roles"] and row["normal_count"] <= MAX_NORMALS
            and row["missing_supers"] == 0 and row["missing_ultimates"] == 0)
        row["status"] = "role_count_complete_mechanics_unverified" if row["has_required_content"] else "incomplete"
    return {"schema": 1,
            "contract": {"normal_total": [5, 6], "neutral_combo": [2, 3],
                         "juggle": 1, "launcher": 1, "wall_carry": 1,
                         "optional_sixth": "extra neutral or separate finisher",
                         "supers": 2, "ultimate": 1, "assists": "separate"},
            "role_classification": "name/purpose inferred only, not verified choreography",
            "roster": roster}


def hit_pose_indices(move: dict) -> list[int]:
    poses = move.get("poses", [])
    if not poses:
        return []
    return sorted({pose_for_tick(poses, int(hit["tick"]))[0]
                   for hit in move.get("hit_events", [])})


def fragment(move: dict, phase: str, selection: str | None = None) -> dict:
    poses = move["poses"]
    hits = hit_pose_indices(move)
    if not hits:
        raise ValueError("No hit-bearing poses: " + move["sequence_id"])
    first, last = min(hits), max(hits)
    if phase == "windup":
        ids = list(range(first)) or [0]
    elif phase == "attack":
        ids = list(range(first, last + 1))
    elif phase == "recovery":
        ids = list(range(last + 1, len(poses))) or [len(poses)-1]
    else:
        raise ValueError(phase)
    if selection == "head" and len(ids) >= 3:
        ids = ids[:3]
    if selection == "tail" and len(ids) >= 3:
        ids = ids[-3:]
    return {"source_sequence_id": move["sequence_id"], "phase": phase,
            "indices": ids, "pose_paths": [poses[i]["path"] for i in ids]}


def recipes_for(character: str, by_id: dict[str, dict]) -> dict[str, list[dict]]:
    group = [m for m in by_id.values()
             if m.get("character") == character and classify(m)]
    source_by_role = {}
    for role in ROLES:
        candidates = sorted((m for m in group if classify(m) == role),
                            key=lambda x: x["sequence_id"])
        if candidates:
            source_by_role[role] = candidates[0]
    if not {"neutral_combo", "juggle", "finisher"}.issubset(source_by_role):
        raise ValueError(f"{character}: need source neutral, juggle and finisher to construct first neutral alternative")
    neutral = source_by_role["neutral_combo"]
    juggle = source_by_role["juggle"]
    finish = source_by_role["finisher"]
    return {
        "precision": [
            fragment(neutral, "windup"),
            fragment(juggle, "attack", "head"),
            fragment(neutral, "attack", "tail"),
            fragment(neutral, "recovery")],
        "rush": [
            fragment(neutral, "windup"),
            fragment(neutral, "attack"),
            fragment(juggle, "attack", "tail"),
            fragment(juggle, "recovery")],
        "finisher": [
            fragment(neutral, "windup"),
            fragment(juggle, "attack", "head"),
            fragment(finish, "attack", "tail"),
            fragment(finish, "recovery")],
    }


def geometry(path: str, cache: dict, root: Path = ROOT) -> dict:
    if path in cache:
        return cache[path]
    if not path.startswith("res://"):
        raise ValueError(f"Disallowed source path: {path}")
    filename = (root / path[6:]).resolve()
    if not filename.is_relative_to(root.resolve()) or not filename.is_file():
        raise ValueError(f"Unknown sprite: {path}")
    with Image.open(filename) as image:
        alpha = image.convert("RGBA").getchannel("A")
        bbox = alpha.getbbox()
        if bbox is None:
            raise ValueError("Transparent sprite: " + path)
        cx = (bbox[0] + bbox[2]) / (2 * image.width)
        cy = (bbox[1] + bbox[3]) / (2 * image.height)
        result = {"width": image.width, "height": image.height, "bbox": list(bbox),
                  "normalized_center": [round(cx, 4), round(cy, 4)],
                  "normalized_height": round((bbox[3]-bbox[1])/image.height, 4)}
    cache[path] = result
    return result


def build_candidate(style: str, fragments: list[dict],
                    by_id: dict[str, dict], root: Path = ROOT) -> dict:
    frames = []
    hit_proposals = []
    beats = []
    issues = []
    geometry_cache = {}
    previous = None
    time = 0
    for order, part in enumerate(fragments):
        donor = by_id[part["source_sequence_id"]]
        phase = part["phase"]
        source_indices = set(part["indices"])
        start = time
        for index in part["indices"]:
            original = donor["poses"][index]
            # Recovery excerpts are short and readable; hit sequences retain source cadence.
            ticks = max(5, min(int(original["ticks"]), 16 if phase != "attack" else 13))
            path = original["path"]
            shape = geometry(path, geometry_cache, root=root)
            if previous is not None:
                dx = shape["normalized_center"][0] - previous["normalized_center"][0]
                dy = shape["normalized_center"][1] - previous["normalized_center"][1]
                dist = math.hypot(dx, dy)
                if dist > 0.20:
                    issues.append({"transition_at": len(frames),
                                   "issue": "large_pose_center_jump",
                                   "normalized_distance": round(dist, 4)})
                if shape["width"] != previous["width"] or shape["height"] != previous["height"]:
                    issues.append({"transition_at": len(frames), "issue": "canvas_dimension_change"})
            previous = shape
            frames.append({"tick_start": time, "ticks": ticks, "pose_path": path,
                           "source_sequence_id": donor["sequence_id"], "source_pose_index": index,
                           "phase_hint": phase, "semantic_confidence": "unverified",
                           "native_facing": original.get("native_facing", 1),
                           "anchor": original.get("anchor"), "offset": original.get("offset", [0, 0])})
            for hit in donor["hit_events"]:
                if phase != "attack" or pose_for_tick(donor["poses"], int(hit["tick"]))[0] != index:
                    continue
                pose_begin = sum(int(p["ticks"]) for p in donor["poses"][:index])
                local = max(0, int(hit["tick"]) - pose_begin)
                event_time = time + min(local, ticks-1)
                hit_proposals.append({
                    "proposal_id": f"{style}_{order}_{hit['id']}",
                    "tick": event_time, "source_hit_id": hit["id"],
                    "source_sequence_id": donor["sequence_id"],
                    "pose_index": len(frames)-1,
                    "target_reaction_reference": hit.get("reaction"),
                    "source_hit_region_reference": hit.get("region"),
                    "damage": None, "contact_verified": False,
                    "audio": {"voice": None, "impact": None, "review_status": "unassigned"}})
            time += ticks
        beats.append({"beat": phase, "source_sequence_id": donor["sequence_id"],
                      "start_tick": start, "end_tick_exclusive": time,
                      "visual_intent": ("windup" if phase == "windup" else
                                        "multiple strikes" if phase == "attack" else "settle")})
    if len(hit_proposals) < 2:
        issues.append({"issue": "less_than_two_hit_proposals"})
    sequence = [f["pose_path"] for f in frames]
    return {"id": f"{by_id[fragments[0]['source_sequence_id']]['character']}_neutral_b_{style}",
            "slot_proposal": "neutral_combo_2", "style": style,
            "status": "UNAPPROVED_STORYBOARD_NOT_GAMEPLAY",
            "source_poses": sequence, "frame_track": frames, "beat_track": beats,
            "impact_proposals": hit_proposals, "duration_ticks": time,
            "visual_warnings": issues,
            "missing": ["confirmed_pose_semantics", "hand_weapon_anchors",
                        "actor_target_motion", "sound_mapping", "damage_balancing",
                        "Godot_hit_validation", "cancel_windows"],
            "revision_rule": "Review artwork/pose continuity and test real contact before compiling a playable move."}


def build(character: str, moves: list[dict] | None = None, root: Path = ROOT) -> dict:
    source = moves if moves is not None else load_moves()
    by_id = {m["sequence_id"]: m for m in source}
    recipes = recipes_for(character, by_id)
    candidates = {style: build_candidate(style, pieces, by_id, root) for style, pieces in recipes.items()}
    uniqueness = {tuple(c["source_poses"]) for c in candidates.values()}
    if len(uniqueness) != 3:
        raise ValueError("Failed to produce genuinely different pose sequences")
    checksum = hashlib.sha256(json.dumps([m for m in source if m.get("character")==character],
                                      sort_keys=True).encode()).hexdigest()
    return {"schema": 1, "character": character, "proposed_role": "neutral_combo_2",
            "source_sha256": checksum, "no_runtime_changes": True,
            "source_fragments": recipes, "candidates": candidates,
            "visual_approval": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", action="append",
                        help="Preview candidate for this character; repeatable")
    parser.add_argument("--out", type=Path, default=ROOT / "docs/director_phrase_reviews")
    args = parser.parse_args()
    moves = load_moves()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    roster = roster_audit(moves)
    (out / "role_coverage.json").write_text(json.dumps(roster, indent=2) + "\n")
    for name in args.character or ["chunli", "dante", "kosmos"]:
        result = build(name, moves)
        target = out / name
        target.mkdir(parents=True, exist_ok=True)
        (target / "storyboards.json").write_text(json.dumps(result, indent=2) + "\n")
        print(f"{name}: 3 distinct unapproved neutral-combo storyboards; "
              f"frame counts {[len(c['frame_track']) for c in result['candidates'].values()]}")
    print(f"Coverage: {len(roster['roster'])} characters, "
          f"{sum(int(r['has_required_content']) for r in roster['roster'].values())} "
          "have all role counts (visual quality not assessed)")


if __name__ == "__main__":
    main()
