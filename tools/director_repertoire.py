#!/usr/bin/env python3
"""Director Repertoire Registry: all-16 fighter design identities and actual asset provenance.

No canon claims, animation semantics or contact validation are inferred from filenames.
No writes to .tres, gameplay registries, master timelines, or character assets.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'moves/choreography.json'
BLUEPRINT = ROOT / 'moves/director_identity_blueprints.json'
MAIN_SLOTS = ('neutral_a', 'neutral_b', 'juggle', 'launcher', 'wall_carry', 'finisher')
SUPER_SLOTS = ('super_a', 'super_b')
ALL_SLOTS = MAIN_SLOTS + SUPER_SLOTS + ('ultimate',)


def paths(move: dict) -> list[str]:
    return [p['path'] for p in move.get('poses', [])]


def contact_pose_paths(move: dict) -> list[str]:
    poses = move.get('poses') or []
    at = 0
    boundaries = []
    for pose in poses:
        at += int(pose['ticks'])
        boundaries.append(at)
    contacts = []
    for event in move.get('hit_events', []):
        tick = int(event['tick'])
        if tick < 0 or tick >= at:
            raise ValueError(f"Bad hit tick for {move.get('sequence_id')}: {tick}")
        index = next(i for i, end in enumerate(boundaries) if tick < end)
        contacts.append(poses[index]['path'])
    return contacts


def common_run(a: list[str], b: list[str]) -> int:
    previous = [0] * (len(b) + 1)
    longest = 0
    for x in a:
        current = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            if x == y:
                current[j] = previous[j-1] + 1
                longest = max(longest, current[j])
        previous = current
    return longest


def motif_fingerprint(move: dict) -> dict:
    frame_seq = paths(move)
    hits = contact_pose_paths(move)
    return {
        'move': move['sequence_id'], 'source_frames': len(frame_seq),
        'distinct_source_frames': len(set(frame_seq)),
        'hit_source_paths': hits, 'source_pose_paths': frame_seq,
        'hit_motif_sha256': hashlib.sha256('\n'.join(hits).encode()).hexdigest(),
        'status': 'SOURCE_IDENTITY_ONLY_UNVERIFIED_SEMANTICS'
    }


def role_assignment(move: dict) -> str | None:
    if move.get('role') != 'main':
        return None
    category = move.get('category')
    name = move['sequence_id']
    suffix = name.split('_')[-1]
    if category == 'special':
        if suffix == '1': return 'super_a'
        if suffix == '2': return 'super_b'
    if category == 'ultimate': return 'ultimate'
    if category != 'normal': return None
    if suffix in ('neutral', 'arc'): return 'neutral_a'
    if suffix in ('left', 'barrage'): return 'juggle'
    if suffix == 'up': return 'launcher'
    if suffix == 'right': return 'wall_carry'
    if suffix == 'down': return 'finisher'
    return None


def collisions(moves: list[dict]) -> list[dict]:
    """Human review risks, not a proof that two attacks are the same move."""
    pairs = []
    for i, a in enumerate(moves):
        for b in moves[i+1:]:
            if a['character'] != b['character']:
                continue
            if a.get('category') not in ('normal','special','ultimate') or b.get('category') not in ('normal','special','ultimate'):
                continue
            pa, pb = paths(a), paths(b)
            ha, hb = contact_pose_paths(a), contact_pose_paths(b)
            shared_run = common_run(pa, pb)
            common_hits = len(set(ha) & set(hb))
            hit_overlap = common_hits / len(set(ha) | set(hb)) if (ha or hb) else 0
            same_ordered_strikes = bool(len(ha) >= 2 and ha == hb)
            severity = 'needs_art_review' if (shared_run >= 4 or hit_overlap >= .60 or same_ordered_strikes) else 'low'
            if severity == 'low':
                continue
            pairs.append({
                'a': a['sequence_id'], 'b': b['sequence_id'],
                'shared_contiguous_source_poses': shared_run,
                'contact_pose_jaccard': round(hit_overlap, 3),
                'identical_ordered_contact_sources': same_ordered_strikes,
                'severity': severity,
                'limitation': 'Frame-path similarity does not establish that different sprites depict the same martial-arts technique.'
            })
    return sorted(pairs, key=lambda row:(-row['shared_contiguous_source_poses'], -row['contact_pose_jaccard'],row['a'],row['b']))


def sprite_inventory(moves: list[dict], root: Path) -> dict:
    used = sorted({p for m in moves for p in paths(m)})
    directories = sorted({str(Path(p.removeprefix('res://')).parent) for p in used if p.startswith('res://')})
    available = set()
    for directory in directories:
        source = (root / directory).resolve()
        if not source.is_relative_to(root.resolve()):
            raise ValueError('Unsafe sprite directory: ' + directory)
        if source.is_dir():
            available.update('res://' + str(path.relative_to(root)).replace('\\','/')
                             for path in source.glob('*.png') if path.is_file())
    missing = [p for p in used if not (root / p.removeprefix('res://')).is_file()]
    return {'used_pose_count':len(used), 'available_png_count':len(available),
            'unreferenced_png_count':len(available-set(used)),
            'unreferenced_sample':sorted(available-set(used))[:18],
            'source_directories':directories,'missing_source_files':missing,
            'status':'FRAME_PRESENCE_NOT_POSE_CLASSIFICATION'}


def compile_registry(source: dict, blueprint: dict, root: Path = ROOT) -> dict:
    moves = source['moves']
    names = sorted({m['character'] for m in moves if m['character'] != 'placeholder_cpu'})
    if set(names) != set(blueprint['characters']):
        raise ValueError('Blueprint and source fighter IDs differ: ' + repr((names,sorted(blueprint['characters']))))
    if len(names) != 16:
        raise ValueError('Expected exact 16-fighter source registry')
    result = {}
    for name in names:
        authored = [m for m in moves if m['character'] == name]
        main = [m for m in authored if m.get('role')=='main']
        slots = {slot:[] for slot in ALL_SLOTS}
        extras = []
        for move in main:
            assigned = role_assignment(move)
            (slots[assigned] if assigned in slots else extras).append(move['sequence_id'])
        concept = blueprint['characters'][name]
        plan = {}
        for slot in ALL_SLOTS:
            src = slots[slot]
            if len(src)>1:
                raise ValueError(f'Double-booked {name} {slot}: {src}')
            identity=concept['slots'][slot]
            plan[slot] = {
                'design_intent':identity['unique_identity'],
                'design_confidence':identity['status'],
                'source_moves':src,
                'source_classification':'inferred_from_existing_id_not_verified',
                'asset_binding':'existing_unreviewed' if src else 'UNASSIGNED',
                'contact_verified':False,
                'duration_target_ticks':[120,300] if slot in MAIN_SLOTS else None,
                'original_choreography_approved':False,
            }
        issues = collisions(main)
        inventory = sprite_inventory(authored,root)
        fingerprint={m['sequence_id']:motif_fingerprint(m) for m in main}
        normal_filled=sum(bool(slots[s]) for s in MAIN_SLOTS)
        result[name]={
            'design_archetype': concept['archetype_intent'],
            'rhythm_direction': concept['rhythm_direction'],
            'identity_status':'UNVERIFIED_DESIGN_BLUEPRINT',
            'role_slots':plan,
            'filled_main_normals':normal_filled,
            'missing_minimum_normals':[s for s in MAIN_SLOTS if s!='finisher' and not slots[s]],
            'missing_supers':[s for s in SUPER_SLOTS if not slots[s]],
            'missing_ultimate':not bool(slots['ultimate']),
            'mechanical_role_verified':False,
            'existing_main_fingerprints': fingerprint,
            'reuse_review':issues,
            'sprite_inventory':inventory,
            'extras_unclassified':extras,
            'production_status':'DRAFT_NOT_COMPLETE',
        }
    total_missing=sum(len(x['missing_minimum_normals'])+len(x['missing_supers'])+int(x['missing_ultimate']) for x in result.values())
    return {
        'schema_version':1,
        'source_sha256':hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest(),
        'blueprint_sha256':hashlib.sha256(json.dumps(blueprint,sort_keys=True).encode()).hexdigest(),
        'kind':'READ_ONLY_MOVEMENT_VOCABULARY_AND_COVERAGE_AUDIT',
        'no_playable_moves_created':True,
        'canonical_accuracy':'NOT_RESEARCH_VERIFIED',
        'quality_gate':'Full sprite semantics + originality + real Godot target contact + visual human acceptance required',
        'normal_duration_ticks':[120,300],
        'characters':result,
        'summary':{'fighters':len(result),'missing_required_role_slots':total_missing,
                   'existing_main_movements':sum(len(v['existing_main_fingerprints']) for v in result.values()),
                   'cross_move_reuse_flags':sum(len(v['reuse_review']) for v in result.values()),
                   'known_available_sprite_count':sum(v['sprite_inventory']['available_png_count'] for v in result.values()),
                   'unreferenced_sprite_count':sum(v['sprite_inventory']['unreferenced_png_count'] for v in result.values()),
                   'players_completely_research_verified':0}
    }


def render_html(registry: dict) -> str:
    blocks=[]
    for key, c in registry['characters'].items():
        flags=c['reuse_review'][:8]
        issues=''.join(f'<li>{html.escape(f["a"])} vs {html.escape(f["b"])}: '+
                      f'{f["shared_contiguous_source_poses"]} shared frames, '+
                      f'{f["contact_pose_jaccard"]} contact overlap</li>' for f in flags)
        slots=''.join('<tr><td>'+html.escape(slot)+'</td><td>'+html.escape(data['design_intent'])+
                      '</td><td>'+html.escape(', '.join(data['source_moves']) or 'UNASSIGNED')+'</td></tr>'
                      for slot,data in c['role_slots'].items())
        blocks.append('<details><summary>'+html.escape(key)+' — '+str(c['filled_main_normals'])+
                      '/6 existing normal roles, '+str(len(c['reuse_review']))+' reuse flags, '+
                      str(c['sprite_inventory']['unreferenced_png_count'])+' unreferenced source PNGs</summary>'+
                      '<p>'+html.escape(c['design_archetype'])+' · '+html.escape(c['rhythm_direction'])+'</p>'+
                      '<table><tr><th>Slot</th><th>Distinct intended identity (unverified)</th><th>Existing move reference</th></tr>'+slots+'</table>'+
                      '<p><b>Potential reuse:</b> <ul>'+issues+'</ul></p></details>')
    return ('<!doctype html><meta charset="utf-8"><title>Director Repertoire Registry — 16 Fighters</title>'+
            '<style>body{margin:2rem auto;max-width:1150px;padding:12px;background:#0e1624;color:#e9f2fb;font:14px system-ui}' +
            'details{border:1px solid #485f75;border-radius:10px;padding:12px;margin:12px 0}summary{font-size:17px;cursor:pointer}' +
            'table{border-collapse:collapse;width:100%;margin:14px 0}th,td{border:1px solid #485f75;padding:9px;text-align:left}' +
            'em{color:#f9ce80}</style><h1>Choreography Director · All-16 Repertoire Registry</h1>' +
            '<p><em>DESIGN HYPOTHESES, NOT CANON VERIFIED.</em> Every entry is an authoring contract, not a completed move. ' +
            'Frame reuse flags compare files, not physical techniques. No player-facing content was installed.</p>'+
            '<p>Unreferenced images are inventory leads, not verified attacks. Review sprite pose meaning and contact before using.</p>'+
            ''.join(blocks))


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=SOURCE)
    p.add_argument('--blueprint',type=Path,default=BLUEPRINT)
    p.add_argument('--out',type=Path,default=ROOT/'docs/director_repertoire_audit')
    args=p.parse_args()
    data=compile_registry(json.loads(args.source.read_text()),json.loads(args.blueprint.read_text()),ROOT)
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'repertoire.json').write_text(json.dumps(data,indent=2)+'\n')
    (args.out/'review.html').write_text(render_html(data))
    print('REPERTOIRE:',json.dumps(data['summary'],sort_keys=True))

if __name__=='__main__':main()
