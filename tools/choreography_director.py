#!/usr/bin/env python3
"""Choreography Director Phase 1: non-destructive candidate timing studies.

Never mutates moves/choreography.json or gameplay Resources. Candidate frames
stay in the original order; this is NOT an animation reconstruction model.
"""
from __future__ import annotations
import argparse, copy, html, json, math
from pathlib import Path
from statistics import mean, pstdev

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / 'moves' / 'choreography.json'
DEFAULT_DIR = ROOT / 'docs' / 'director_drafts'


def load_moves(path: Path = MASTER) -> list[dict]:
    doc = json.loads(path.read_text(encoding='utf-8'))
    assert isinstance(doc.get('moves'), list), 'Missing moves array'
    return doc['moves']


def pose_for_tick(poses: list[dict], tick: int) -> tuple[int, int]:
    at = 0
    for idx, pose in enumerate(poses):
        n = int(pose['ticks'])
        if at <= tick < at + n:
            return idx, tick-at
        at += n
    raise ValueError(f'Hit tick {tick} outside pose track length {at}')


def retime(values: list[int], weights: list[float], total: int, minimum: int = 3) -> list[int]:
    """Integer largest-remainder apportionment, preserving exact total/minima."""
    if not values or len(values) != len(weights) or total < minimum*len(values):
        raise ValueError('Impossible pose budget')
    free = total - minimum * len(values)
    scaled = [max(0.0, (v-minimum)*w) for v,w in zip(values,weights)]
    if not any(scaled): scaled = [1.0] * len(values)
    s = sum(scaled)
    exact = [free*x/s for x in scaled]
    ints = [minimum + int(x) for x in exact]
    remaining = total - sum(ints)
    order = sorted(range(len(values)), key=lambda i:(exact[i]-int(exact[i]),-i), reverse=True)
    for idx in order[:remaining]:
        ints[idx] += 1
    assert sum(ints) == total and min(ints) >= minimum
    return ints


def map_tick(old: list[int], new: list[int], tick: int) -> int:
    if not old or tick < 0:
        raise ValueError('invalid tick map')
    elapsed = 0
    for i, n in enumerate(old):
        if tick < elapsed + n:
            rel = tick - elapsed
            new_start = sum(new[:i])
            return new_start + min(new[i]-1, int(round(rel / max(1,n-1) * (new[i]-1))))
        elapsed += n
    return sum(new)-1


def make_candidate(move: dict, variant: str) -> dict:
    """Only retimes pose track and tick-based events; never adds hits/damage."""
    m = copy.deepcopy(move)
    if variant == 'source':
        return m
    if m.get('category') != 'normal' or not m.get('poses') or not m.get('hit_events'):
        raise ValueError('Draft retiming is restricted to existing non-cinematic normal attacks')
    old = [int(p['ticks']) for p in m['poses']]
    contact = {pose_for_tick(m['poses'], int(e['tick']))[0] for e in m['hit_events']}
    first = min(contact); last = max(contact)
    weights=[]
    for i in range(len(old)):
        if variant == 'snap':
            weights.append(1.12 if i<first else (0.77 if i in contact else (1.28 if i>last else 0.94)))
        elif variant == 'heavy':
            weights.append(1.25 if i<first else (1.15 if i in contact else (0.88 if i>last else 0.89)))
        else:
            raise ValueError(f'Unknown variant: {variant}')
    new = retime(old, weights, int(m['duration_ticks']))
    for p,n in zip(m['poses'], new):
        p['ticks']=n
    for ev in m['hit_events']:
        start=int(ev['tick']); end=int(ev.get('end_tick',start)); length=end-start
        at=map_tick(old,new,start)
        ev['tick']=at
        # Maintain original active window length if possible, never cross into next beat's pose.
        idx,_=pose_for_tick(m['poses'],at)
        limit=sum(new[:idx+1])-1
        ev['end_tick']=min(at+length, limit, m['duration_ticks']-1)
    for cue in m.get('cues',[]):
        if 'tick' in cue: cue['tick']=map_tick(old,new,int(cue['tick']))
    for motion in m.get('movement',[]):
        for key in ('tick','start_tick','end_tick'):
            if key in motion: motion[key]=map_tick(old,new,int(motion[key]))
    # Retiming stage gate windows is delicate; keep in draft and flag for review.
    m['_director']={'variant':variant,'approval':'needs_visual_review','source_sequence_id':move['sequence_id'],
                    'note':'Generated timing study only. Existing pose order, hits, damage and contact geometry retained. Staging/cancel windows need engine review.',
                    'old_pose_ticks':old,'new_pose_ticks':new}
    return m


def lint(move: dict, root: Path = ROOT) -> tuple[list[str],list[str]]:
    errors=[];warnings=[]
    poses=move.get('poses') or []; hits=move.get('hit_events') or []
    total=int(move.get('duration_ticks',0))
    if total<=0: errors.append('Nonpositive duration')
    if not poses:
        warnings.append('No pose track (perhaps CPU placeholder)')
        return errors,warnings
    lengths=[int(p.get('ticks',0)) for p in poses]
    if any(v<=0 for v in lengths):errors.append('Nonpositive pose frame duration')
    if sum(lengths)!=total:errors.append(f'Pose duration sum {sum(lengths)} != declared {total}')
    paths=[]
    for p in poses:
        path=str(p.get('path',''))
        paths.append(path)
        if not path.startswith('res://') or not (root/path.removeprefix('res://')).is_file():
            errors.append(f'Missing source PNG: {path}')
        if len(p.get('anchor',[]))!=2:errors.append(f'Missing anchor for {path}')
    if len(set(paths))<len(paths):warnings.append('Exact same pose PNG reused in sequence')
    events_seen=set(); old_hits=[]
    for ev in hits:
        token=ev.get('id','')
        if not token or token in events_seen:errors.append('Missing/duplicate hit-event ID')
        events_seen.add(token)
        a=int(ev.get('tick',-1)); b=int(ev.get('end_tick',a))
        if a<0 or a>=total or b<a or b>=total: errors.append(f'Invalid hit interval {a}..{b}'); continue
        old_hits.append(a)
        if ev.get('kind','melee')=='melee' and len(ev.get('region',[]))!=4:errors.append('Invalid melee hit region')
        try:
            idx,_=pose_for_tick(poses,a)
            if lengths[idx]>24: warnings.append(f'Hit {token} on long held pose {idx} ({lengths[idx]} ticks)')
        except ValueError as e:errors.append(str(e))
    if old_hits and len(old_hits)>=2:
        gap=[y-x for x,y in zip(sorted(old_hits),sorted(old_hits)[1:])]
        if max(gap)>45:warnings.append('Large empty interval between hits')
        if max(old_hits)<total*.60:warnings.append('Last hit occurs before 60% of duration (check recovery pacing)')
    if move.get('_director'):warnings.append('Unapproved director draft; no automatic gameplay sign-off')
    return errors,sorted(set(warnings))


def metrics(move: dict) -> dict:
    ticks=[int(p['ticks']) for p in move['poses']]
    hits=sorted(int(e['tick']) for e in move['hit_events'])
    gaps=[b-a for a,b in zip(hits,hits[1:])]
    first=hits[0] if hits else None
    last=hits[-1] if hits else None
    unique=len({p['path'] for p in move['poses']})
    return {'duration':move['duration_ticks'],'poses':len(ticks),'unique_poses':unique,
            'hits':len(hits),'first_hit_tick':first,'final_hit_tick':last,
            'recovery_ticks':int(move['duration_ticks']-last) if last is not None else None,
            'hit_gaps_ticks':gaps,'gap_variation':round(pstdev(gaps),2) if len(gaps)>1 else None,
            'pose_ticks':ticks}


def generate_preview(move:dict,candidates:dict, out:Path, root:Path=ROOT):
    """Self-contained JS preview, local PNGs remain linked via project-relative paths."""
    rel_root=Path(__import__('os').path.relpath(root,out)).as_posix()
    data={}
    for key,m in candidates.items():
        data[key]={'poses':[{'path':f'{rel_root}/{p["path"].removeprefix("res://")}', 'ticks':p['ticks']} for p in m['poses']],
                   'hits':[int(e['tick']) for e in m['hit_events']], 'duration':int(m['duration_ticks'])}
    blob=json.dumps(data,ensure_ascii=True).replace('</','<\\/')
    title=html.escape(move.get('display_name',move['sequence_id']))
    content='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Choreography Director — MOVE_TITLE</title><style>
body{margin:0;background:#101624;color:#edf2ff;font:15px system-ui, sans-serif}main{max-width:980px;margin:0 auto;padding:24px}
.controls{display:flex;gap:12px;flex-wrap:wrap;align-items:center}button,select{background:#25334b;color:white;border:1px solid #617293;border-radius:8px;padding:9px;cursor:pointer}
#stage{height:310px;background:radial-gradient(ellipse at 50% 120%,#273951,#131d30);border-radius:14px;display:grid;place-items:center;position:relative;margin-top:18px}
#sprite{width:auto;height:auto;max-height:275px;max-width:500px;object-fit:contain;image-rendering:pixelated}
#hit{position:absolute;inset:0;pointer-events:none;opacity:0;background:radial-gradient(circle,#ffe7af28,transparent 48%)}
small{color:#a9bad3} .timeline{height:24px;background:#28374e;margin:16px 0;position:relative;border-radius:4px;overflow:hidden}
.beat{position:absolute;top:0;bottom:0;border-right:1px solid #889ac4;background:#627ba030}.marker{position:absolute;top:0;bottom:0;width:3px;background:#ffd166}
#readout{font-variant-numeric:tabular-nums}</style><main><h2>Choreography Director · MOVE_TITLE</h2>
<p>Draft timing study, not an approved animation. Frames and hit geometry are borrowed unchanged from the current project.</p>
<div class="controls"><label>Variant <select id="variant"><option value="source">Original</option><option value="snap">Snap</option><option value="heavy">Heavy</option></select></label>
<button id="play">Play</button><button id="step">+1 tick</button><label>Speed <select id="speed"><option value=".25">¼×</option><option value=".5">½×</option><option selected value="1">1×</option></select></label><span id="readout"></span></div>
<div id="stage"><img id="sprite" alt="Current sprite pose"><div id="hit"></div></div><div class="timeline" id="timeline"></div>
<small>Yellow ticks are hit events. The flash is a visualization of timing only; no damage is simulated. Open this HTML from the extracted Godot project folder.</small>
<script>const BANK=JSON_DATA;let playing=false,last=0,tick=0;const $=s=>document.querySelector(s);let settings=BANK.source;
function draw(){let at=0,idx=0;for(let i=0;i<settings.poses.length;i++){const n=Number(settings.poses[i].ticks);if(tick<at+n){idx=i;break}at+=n}
$('#sprite').src=settings.poses[idx].path;$('#readout').textContent=`Tick ${tick}/${settings.duration-1} · Pose ${idx+1}/${settings.poses.length}`;const hit=settings.hits.includes(Math.floor(tick));$('#hit').style.opacity=hit?1:0;}
function bars(){let t=$('#timeline');t.innerHTML='';let at=0;for(const p of settings.poses){const e=document.createElement('div');e.className='beat';e.style.left=(at/settings.duration*100)+'%';e.style.width=(p.ticks/settings.duration*100)+'%';t.append(e);at+=p.ticks}for(const x of settings.hits){const e=document.createElement('div');e.className='marker';e.style.left=(x/settings.duration*100)+'%';t.append(e)}}
$('#variant').addEventListener('change',()=>{settings=BANK[$('#variant').value];tick=0;bars();draw()});$('#play').onclick=()=>{playing=!playing;$('#play').textContent=playing?'Pause':'Play';last=0};$('#step').onclick=()=>{playing=false;$('#play').textContent='Play';tick=(tick+1)%settings.duration;draw()};
function animate(ts){if(playing){if(!last)last=ts;const dt=ts-last;let advance=Math.floor(dt/(1000/(60*Number($('#speed').value))));if(advance){tick=(tick+advance)%settings.duration;last+=advance*1000/(60*Number($('#speed').value));draw()}}else{last=0}requestAnimationFrame(animate)}bars();draw();requestAnimationFrame(animate);</script></main></html>'''
    (out/'preview.html').write_text(content.replace('MOVE_TITLE',title).replace('JSON_DATA',blob),encoding='utf-8')


def generate(move: dict, output:Path, root:Path=ROOT)->dict:
    if move.get('category')!='normal' or len(move.get('poses',[]))<2 or len(move.get('hit_events',[]))<2:
        raise ValueError('Only existing multi-pose normal attacks supported in Phase 1')
    errors,_=lint(move,root)
    if errors: raise ValueError(f'Source move fails lint: {errors[:4]}')
    output.mkdir(parents=True,exist_ok=True)
    variants={k:make_candidate(move,k) for k in ('source','snap','heavy')}
    results={}
    for k,candidate in variants.items():
        errs,warns=lint(candidate,root)
        (output/f'{k}.json').write_text(json.dumps(candidate,indent=2)+'\n',encoding='utf-8')
        results[k]={'errors':errs,'warnings':warns,'metrics':metrics(candidate)}
    generate_preview(move,variants,output,root)
    report={'source_sequence_id':move['sequence_id'],'project_source':'moves/choreography.json',
            'mode':'non_destructive_proposal','approval':'NOT_APPROVED','candidates':results,
            'limits':['No pose reorder, procedural new animation, semantic sprite tagging or audio assignment',
                      'Contact shape, target physics, hit damage, staging and cancel windows unchanged',
                      'Browser preview is not a Godot gameplay test or proof of contact']}
    (output/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--move',action='append',help='Sequence ID; repeat to generate multiple')
    parser.add_argument('--output',type=Path,default=DEFAULT_DIR)
    parser.add_argument('--audit-all',action='store_true')
    args=parser.parse_args()
    items=load_moves()
    if args.audit_all:
        report={m['sequence_id']:{'errors':lint(m)[0],'warnings':lint(m)[1], 'metrics':metrics(m) if m.get('poses') else {}} for m in items}
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'full_roster_audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print('Audited',len(items),'timelines; structural errors',sum(bool(x['errors']) for x in report.values()))
    ids=args.move or ([] if args.audit_all else ['chunli_neutral','dante_neutral','kosmos_arc'])
    available={m['sequence_id']:m for m in items}
    for sid in ids:
        if sid not in available: parser.error(f'Unknown move {sid}')
        dest=args.output/sid
        result=generate(available[sid],dest)
        print('Generated',sid,'->',dest,'checks:',{v:len(item['errors']) for v,item in result['candidates'].items()})

if __name__=='__main__':main()
