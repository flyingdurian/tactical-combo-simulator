#!/usr/bin/env python3
"""Self-contained private HTML player for role-aware, unapproved pose storyboards."""
from __future__ import annotations
import base64
import html
import io
import json
from pathlib import Path
from PIL import Image


def render_review(review: dict, output: Path, root: Path) -> None:
    images: dict[str, str] = {}
    for candidate in review["candidates"].values():
        for frame in candidate["frame_track"]:
            path = frame["pose_path"]
            if path in images:
                continue
            if not path.startswith("res://"):
                raise ValueError("Unsupported sprite path")
            file = (root / path[6:]).resolve()
            if not file.is_relative_to(root.resolve()):
                raise ValueError("Source outside project")
            with Image.open(file) as raw:
                picture = raw.convert("RGBA")
                picture.thumbnail((280, 230), Image.Resampling.NEAREST)
                canvas = Image.new("RGBA", (300, 250))
                x = (300 - picture.width) // 2
                y = 246 - picture.height
                canvas.alpha_composite(picture, (x, y))
                buf = io.BytesIO()
                canvas.save(buf, format="PNG", optimize=True)
                images[path] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    content = {
        "character": review["character"], "source_sha256": review["source_sha256"],
        "role": review["proposed_role"], "images": images,
        "candidates": review["candidates"], "visual_approval": False
    }
    payload = json.dumps(content, separators=(",", ":"), ensure_ascii=True).replace("</", "<\\/")
    doc = r'''<!doctype html><html lang="en"><meta charset="utf-8">
<title>Director · Alternative combo poses</title>
<style>
*{box-sizing:border-box}body{background:#101824;color:#e7f1fa;max-width:1180px;
margin:25px auto;padding:12px;font:15px system-ui,sans-serif}
h1{font-size:25px}h2{font-size:18px;margin:0 0 10px}
small,.sub{color:#b9c7da}.warning{color:#ffc789}
.panels{display:grid;grid-template-columns:repeat(auto-fit,minmax(285px,1fr));gap:15px}
.panel{border:1px solid #49596c;background:#1c293a;padding:16px;border-radius:12px}
.sprite{height:260px;width:100%;background:#142031;border-radius:8px;object-fit:contain;image-rendering:pixelated}
button{padding:8px 14px;background:#29496b;border:1px solid #7392ac;border-radius:6px;
color:white;cursor:pointer;margin:5px 4px 5px 0}
input[type=range]{width:100%}.meta{height:75px;line-height:1.4;margin-top:7px;overflow:auto}
strong{font-weight:650}.event{color:#ffcc71}
</style>
<h1>Choreography Director · Alternate neutral combos</h1>
<p class="warning"><strong>UNAPPROVED STORYBOARDS</strong> — these use real sprite poses in new
orders. Neither contacts nor believable transitions are verified. No gameplay resources
or damage values have been changed.</p>
<p class="sub">Playback runs at the project's 60-tick rhythm. Check the motion carefully:
silhouette jumps, teleporting feet, awkward weapon movement and incorrect strike poses
must be corrected before a candidate can become a real move.</p>
<div class="panels" id="panels"></div>
<p class="sub">The red review status cannot be changed here. Source provenance and all hit
proposals are in storyboards.json. These animations are private development material,
not game-release content.</p>
<script type="application/json" id="review-data">'''
    doc += payload
    doc += r'''</script>
<script>
const data=JSON.parse(document.getElementById('review-data').textContent);
const holder=document.getElementById('panels');
Object.entries(data.candidates).forEach(([name, move])=>{
  const panel=document.createElement('section');
  panel.className='panel';
  panel.innerHTML='<h2></h2><img class="sprite" alt="current character pose">'
      +'<div><button class="toggle">Play</button><button class="reset">Reset</button></div>'
      +'<input class="seek" type="range" min="0" max="100" value="0">'
      +'<div class="meta"></div><p class="warning"></p>';
  panel.querySelector('h2').textContent=name.toUpperCase();
  panel.querySelector('.warning').textContent=
       move.visual_warnings.length+' continuity warning(s) · not gameplay approved';
  const img=panel.querySelector('img');
  const seek=panel.querySelector('.seek');
  const info=panel.querySelector('.meta');
  const toggle=panel.querySelector('.toggle');
  const reset=panel.querySelector('.reset');
  seek.max=Math.max(0,move.duration_ticks-1);
  let running=false, last=null, tick=0;
  const frames=move.frame_track;
  function show(){
    const here=Math.min(move.duration_ticks-1,Math.max(0,Math.floor(tick)));
    let frame=frames[frames.length-1];
    for(const f of frames) if(here>=f.tick_start && here<f.tick_start+f.ticks){frame=f;break}
    img.src=data.images[frame.pose_path];
    seek.value=here;
    const hits=move.impact_proposals.filter(h=>Math.abs(h.tick-here)<=1);
    info.textContent='Tick '+here+'/'+move.duration_ticks
       +' · '+frame.phase_hint+' · '+frame.source_sequence_id
       +' frame '+frame.source_pose_index;
    if(hits.length){
       const p=document.createElement('div');
       p.className='event';
       p.textContent='Proposed hit marker: '+hits.map(h=>h.source_hit_id).join(', ')
                     +' (unverified contact)';
       info.appendChild(p);
    }
  }
  function step(now){
    if(!running)return;
    if(last!==null)tick+=(now-last)*.060;
    last=now;
    if(tick>=move.duration_ticks){tick=0;running=false;toggle.textContent='Play';}
    show();
    if(running)requestAnimationFrame(step);
  }
  toggle.onclick=()=>{running=!running;last=null;toggle.textContent=running?'Pause':'Play';
                       if(running)requestAnimationFrame(step)};
  reset.onclick=()=>{running=false;last=null;tick=0;toggle.textContent='Play';show()};
  seek.oninput=()=>{running=false;last=null;tick=Number(seek.value);
                    toggle.textContent='Play';show()};
  holder.appendChild(panel);
  show();
});
</script></html>'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(doc, encoding="utf-8")
