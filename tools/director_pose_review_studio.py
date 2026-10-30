#!/usr/bin/env python3
"""Offline visual pose reviewer for 16 fighters (no server, no gameplay writes).

Generates local review pages with exact resized copies of source sprite PNGs.
Reviewer must choose role, mark an anchor and describe inspected evidence;
unreviewed poses are never auto-certified.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path

from tools.director_pose_vocabulary import ROOT, SOURCE, BLUEPRINT, collect_vocabulary


def _safe_thumb(path: str, root: Path, out: Path) -> tuple[str, list[int]]:
    if not path.startswith("res://"):
        raise ValueError("Expected local source sprite")
    target = (root / path[6:]).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError("Unsafe source sprite: " + path)
    from PIL import Image
    with Image.open(target) as source:
        img = source.convert("RGBA")
        img.thumbnail((176, 176), Image.Resampling.NEAREST)
        dimensions = list(img.size)
        fingerprint = hashlib.sha256(path.encode()).hexdigest()[:20]
        dest = out / "thumbs" / (fingerprint + ".png")
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            img.save(dest, optimize=True)
    return "../thumbs/" + dest.name, dimensions


def fighter_html(name: str, poses: dict, images: dict, summary: dict) -> str:
    cards = []
    for index, (path, data) in enumerate(sorted(poses.items())):
        url, display = images[path]
        width, height = data["pixels"]["canvas"]
        hit_count = len(data["hit_event_refs"])
        uses = ", ".join(sorted({u["move"] for u in data["source_uses"]}))
        card = f'''<article class="card" data-index="{index}">
 <header><strong>{html.escape(path.split("/")[-1])}</strong>
 <small>{hit_count} hit-timed source event(s)</small></header>
 <figure><img data-path="{html.escape(path, quote=True)}" src="{html.escape(url, quote=True)}"
 width="{display[0]}" height="{display[1]}" alt="Source pose" title="Click for contact anchor"></figure>
 <div class="anchor">Anchor: not selected</div>
 <label>Visual pose role <select class="role"><option value="">Unreviewed</option>
 <option value="anticipation">Anticipation</option><option value="approach">Approach</option>
 <option value="strike">Striking limb / weapon</option><option value="follow_through">Follow-through</option>
 <option value="recovery">Recovery</option><option value="guard">Guard</option>
 <option value="airborne">Airborne</option><option value="hold">Hold</option>
 <option value="effect_only">Effect only</option></select></label>
 <label>Inspection evidence <textarea class="evidence" rows="2"
 placeholder="Describe the limb/weapon, visible pose and contact point"></textarea></label>
 <label class="approve"><input class="approved" type="checkbox"> Explicitly mark inspected</label>
 <details><summary>Source provenance</summary><small>{html.escape(uses)}</small></details>
 </article>'''
        cards.append(card)
    info = {
        "fighter": name,
        "source_pose_metadata": {
            path: {"canvas": row["pixels"]["canvas"], "hit_events": row["hit_event_refs"],
                   "roles_inferred": row["role_inference"],
                   "sources": row["source_uses"]}
            for path, row in poses.items()
        },
    }
    payload = json.dumps(info, separators=(",", ":")).replace("</", "<\\/")
    return ('''<!doctype html><html lang="en"><meta charset="utf-8">
<title>Director Pose Reviewer</title><style>
body{background:#111925;color:#ecf2fa;font:14px system-ui;max-width:1480px;margin:20px auto;padding:12px}
a{color:#b6d8ff}.warning{color:#ffcd80}.top{position:sticky;top:0;background:#182436;padding:12px;z-index:3;
display:flex;gap:10px;flex-wrap:wrap;align-items:center;border-radius:10px}
input,select,textarea,button{font:inherit;color:#f0f4fa;background:#27394f;border:1px solid #617990;
border-radius:5px;padding:6px}.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(235px,1fr));gap:12px;margin-top:15px}
.card{border:1px solid #3a536d;border-radius:10px;background:#1b2a3d;padding:10px;display:flex;
flex-direction:column;gap:9px}header{display:flex;flex-direction:column;gap:4px}
header strong{overflow-wrap:anywhere}figure{background:#0c1522;height:194px;display:flex;align-items:center;
justify-content:center;margin:0}figure img{object-fit:contain;image-rendering:pixelated;cursor:crosshair}
label{display:flex;flex-direction:column;gap:5px}.approve{flex-direction:row}
small,details{color:#bfcee2}textarea{width:100%;resize:vertical;box-sizing:border-box}
button{cursor:pointer;background:#285174}.error{color:#ff9ba5}
</style>
<h1 id="heading"></h1>
<p class="warning">ZERO POSES AUTOMATICALLY VERIFIED. Click an actual source image to annotate an
inspected contact pixel, select the correct visible pose role, and write evidence. Only checked,
valid records are exported. This is art-review metadata, not a validated hit or playable move.</p>
<div class="top"><label>Reviewer name <input id="reviewer" placeholder="Name required"></label>
<button id="export">Export inspected records as JSON</button><span id="status"></span>
<a href="../index.html">All fighters</a></div>
<div class="cards">''' + "\n".join(cards) + '''</div>
<script id="metadata" type="application/json">''' + payload + '''</script>
<script>
const state=JSON.parse(document.getElementById("metadata").textContent);
document.getElementById("heading").textContent=state.fighter+" · Source Pose Review";
const cards=[...document.querySelectorAll(".card")];
cards.forEach(card=>{
 const img=card.querySelector("img"), anchor=card.querySelector(".anchor");
 img.addEventListener("click",evt=>{
   const bounds=img.getBoundingClientRect(), raw=state.source_pose_metadata[img.dataset.path].canvas;
   const x=Math.min(raw[0]-1,Math.max(0,Math.floor((evt.clientX-bounds.left)/bounds.width*raw[0])));
   const y=Math.min(raw[1]-1,Math.max(0,Math.floor((evt.clientY-bounds.top)/bounds.height*raw[1])));
   card.dataset.x=x;card.dataset.y=y;anchor.textContent="Source pixel: ("+x+", "+y+")";
 });
});
document.getElementById("export").onclick=()=>{
 const reviewer=document.getElementById("reviewer").value.trim(), annotations={};
 const failures=[];
 if(reviewer.length<2){document.getElementById("status").textContent="Enter a reviewer name";
 return;}
 cards.forEach(card=>{
   if(!card.querySelector(".approved").checked)return;
   const img=card.querySelector("img"),role=card.querySelector(".role").value,
         evidence=card.querySelector(".evidence").value.trim(),
         x=Number(card.dataset.x), y=Number(card.dataset.y);
   if(!role || evidence.length<8 || (role==="strike" && (
        card.dataset.x===undefined || card.dataset.y===undefined))){
     failures.push(img.dataset.path.split("/").pop());return;
   }
   annotations[img.dataset.path]={
     status:"VERIFIED_BY_REVIEWER",pose_role:role,
     contact_anchor_source_px:card.dataset.x===undefined?null:[x,y],
     reviewer,evidence_note:evidence
   };
 });
 if(failures.length){document.getElementById("status").textContent=
     "Incomplete review: "+failures.slice(0,3).join(", ");return}
 if(!Object.keys(annotations).length){document.getElementById("status").textContent=
     "No inspected poses selected";return}
 const record={schema_version:1,characters:{[state.fighter]:annotations}};
 const blob=new Blob([JSON.stringify(record,null,2)],{type:"application/json"});
 const url=URL.createObjectURL(blob);const link=document.createElement("a");link.href=url;
 link.download=state.fighter+"_inspected_pose_reviews.json";link.click();
 setTimeout(()=>URL.revokeObjectURL(url),2000);
 document.getElementById("status").textContent=
   "Exported "+Object.keys(annotations).length+" inspected pose records (not gameplay approved)";
};
</script></html>''')


def emit_studio(report: dict, target: Path, root: Path = ROOT) -> dict:
    """Emit private offline inspection pages with actual thumbnails."""
    target.mkdir(parents=True, exist_ok=True)
    image_cache = {}
    details = []
    for fighter, row in sorted(report["characters"].items()):
        images = {}
        for path in sorted(row["poses"]):
            if path not in image_cache:
                image_cache[path] = _safe_thumb(path, root, target)
            images[path] = image_cache[path]
        page = target / "fighters" / (fighter + ".html")
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(fighter_html(fighter,row["poses"],images,{}),encoding="utf-8")
        details.append(f'<li><a href="fighters/{html.escape(fighter)}.html">{html.escape(fighter)}'
                       f'</a> — {row["pose_count"]} source poses, '
                       f'{row["hit_timed_pose_count"]} hit-timed frames</li>')
    (target/"fighters"/"index.html").write_text(
        "<!doctype html><html lang=en><meta charset=utf-8>"
        "<title>Director Pose Review Studio</title>"
        "<style>body{font:16px system-ui;background:#101a27;color:#edf4fc;max-width:860px;"
        "margin:30px auto}a{color:#aadaff}li{padding:7px}</style>"
        "<h1>Director Pose Review Studio — 16 Fighters</h1>"
        "<p>Private local inspection only. Every pose starts unreviewed. Labels, contact "
        "anchors and reviewer evidence require individual visual inspection.</p><ul>"
        + "".join(details) + "</ul>",
        encoding="utf-8")
    # A root shortcut for non-technical review from a ZIP extraction.
    (target/"index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" '
        'content="0;url=fighters/index.html"><a href="fighters/index.html">'
        'Open Director Studio</a>', encoding="utf-8")
    return {"fighters":len(report["characters"]), "source_thumbnails":len(image_cache),
            "status":"UNREVIEWED_REVIEW_STUDIO"}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,default=ROOT/"docs/director_pose_review_studio")
    args=p.parse_args()
    source=json.loads(SOURCE.read_text(encoding="utf-8"))
    blueprint=json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    vocab=collect_vocabulary(source,blueprint,ROOT)
    print("Pose Review Studio:",emit_studio(vocab,args.out))


if __name__=="__main__":
    main()
