#!/usr/bin/env python3
"""Non-destructive semantic pose / hit review for the Choreography Director.

The tool never guesses sprite actions or modifies combat timelines. It generates
review templates, then checks human- or vision-verified pose tags against events.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTACT_TAGS = frozenset({'contact', 'weapon_contact', 'projectile_release', 'beam_exposure'})
STAGES = frozenset({'unknown', 'anticipation', 'approach', 'contact', 'follow_through', 'recovery', 'airborne', 'hold'})


def pose_at(poses: list[dict], tick: int) -> int:
    start = 0
    for i, pose in enumerate(poses):
        end = start + int(pose['ticks'])
        if start <= tick < end:
            return i
        start = end
    raise ValueError(f'tick {tick} outside pose track [0,{start})')


def review_template(move: dict) -> dict:
    """Build metadata-only review; every unknown remains explicitly unknown."""
    poses = move.get('poses') or []
    events = move.get('hit_events') or []
    evidence = []
    for ev in events:
        tick = int(ev['tick'])
        index = pose_at(poses, tick)
        evidence.append({'event_id': ev['id'], 'tick': tick,
                         'pose_index': index, 'pose_path': poses[index]['path'],
                         'approved_contact': False, 'review_notes': ''})
    return {'schema_version': 1, 'sequence_id': move['sequence_id'],
            'source_duration_ticks': move['duration_ticks'],
            'source_pose_count': len(poses),
            'poses': [{'index': i, 'path': p['path'], 'stage': 'unknown',
                       'tags': [], 'foot_anchor': None, 'contact_anchor': None,
                       'confidence': 'unreviewed', 'notes': ''}
                      for i,p in enumerate(poses)],
            'hit_evidence': evidence, 'approved': False}


def evaluate(move: dict, review: dict) -> dict:
    """Gate approval on explicit pose/evidence, not a plausible numeric score."""
    errors = []
    warnings = []
    if review.get('sequence_id') != move.get('sequence_id'):
        errors.append('Sequence identity mismatch')
    poses = move.get('poses') or []
    if len(review.get('poses', [])) != len(poses):
        errors.append('Pose count mismatch')
    if review.get('source_duration_ticks') != move.get('duration_ticks'):
        errors.append('Source duration changed; regenerate review')
    by_index = {p.get('index'):p for p in review.get('poses', [])}
    for i,pose in enumerate(poses):
        record = by_index.get(i)
        if record is None or record.get('path') != pose.get('path'):
            errors.append(f'Pose {i} source mismatch')
        elif record.get('stage') not in STAGES:
            errors.append(f'Pose {i} invalid stage {record.get("stage")}')
    event_by_id = {e.get('event_id'):e for e in review.get('hit_evidence', [])}
    if len(event_by_id) != len(review.get('hit_evidence', [])):
        errors.append('Duplicate hit evidence IDs')
    for ev in move.get('hit_events', []):
        event_id = ev['id']
        tick = int(ev['tick'])
        index = pose_at(poses,tick)
        evidence = event_by_id.get(event_id)
        if not evidence or evidence.get('tick')!=tick or evidence.get('pose_index')!=index:
            errors.append(f'{event_id}: missing/stale hit-to-pose evidence')
            continue
        pose_review = by_index.get(index, {})
        tags = set(pose_review.get('tags', []))
        if pose_review.get('stage') == 'recovery':
            errors.append(f'{event_id}: hit during recovery-tagged pose')
        if not tags.intersection(CONTACT_TAGS):
            warnings.append(f'{event_id}: pose {index} lacks verified contact/release tag')
        if not evidence.get('approved_contact'):
            warnings.append(f'{event_id}: contact visual not approved')
        if not pose_review.get('contact_anchor'):
            warnings.append(f'{event_id}: contact/release anchor not annotated')
    if not move.get('hit_events'):
        warnings.append('No hit events to review')
    ready = not errors and not warnings and all(
        p.get('confidence') == 'verified' for p in review.get('poses', []))
    return {'sequence_id': move.get('sequence_id'), 'ready_for_visual_approval': ready,
            'errors': errors, 'warnings': warnings,
            'note': 'Semantic check only: actual in-engine alignment and contact must still be reviewed.'}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'moves/choreography.json')
    parser.add_argument('--move', required=True, help='move sequence_id')
    parser.add_argument('--output', type=Path, required=True, help='output JSON review path')
    args=parser.parse_args()
    moves=json.loads(args.source.read_text(encoding='utf-8'))['moves']
    selected=next((m for m in moves if m['sequence_id']==args.move),None)
    if selected is None: parser.error(f'Unknown move: {args.move}')
    if not selected.get('poses'):parser.error('Move does not have poses')
    review=review_template(selected)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
    print(f'Generated unapproved semantic review for {args.move}: {len(review["poses"])} poses, {len(review["hit_evidence"])} hits')

if __name__ == '__main__': main()
