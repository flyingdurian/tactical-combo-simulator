"""Build reviewable timing cards; no quality is inferred from hit counts.
Run: python tools/choreography_review.py [character ID]
"""
from pathlib import Path
from PIL import Image,ImageDraw
import json,sys
root=Path(__file__).resolve().parents[1]
items=json.loads((root/'moves/choreography.json').read_text())['moves']
character=sys.argv[1] if len(sys.argv)>1 else 'chunli'
out=root/'docs'/'choreography_review';out.mkdir(exist_ok=True)
(out/'.gdignore').touch()
rows=['# Choreography review: '+character,'','These cards expose pose order, timing and event placement. They do not certify visual quality. Review anticipation, actual contact, target reaction and recovery at full and quarter speed.','']
for m in items:
 if m['character']!=character:continue
 poses=m['poses'];card=Image.new('RGB',(960,64+((len(poses)+5)//6)*190),'#18212d');draw=ImageDraw.Draw(card);draw.text((12,12),m['display_name'],fill='white');at=0
 for i,p in enumerate(poses):
  x=(i%6)*160;y=64+(i//6)*190
  source=root/p['path'].removeprefix('res://')
  if source.exists():
   image=Image.open(source).convert('RGBA');image.thumbnail((150,145),Image.Resampling.NEAREST);card.paste(image,(x,y),image)
  hits=[str(e['id']) for e in m['hit_events'] if at<=int(e['tick'])<at+int(p['ticks'])]
  draw.text((x+3,y+146),f"{i}: {at}-{at+p['ticks']-1} / face {p.get('native_facing','?')}",fill='white')
  draw.text((x+3,y+162),'HIT' if hits else 'pose',fill='#ffe099');at+=p['ticks']
 name=m['sequence_id']+'.png';card.save(out/name)
 unique=len({p['path'] for p in poses})
 rows.extend([f"## {m['display_name']}",f"{len(poses)} pose beats; {unique} unique poses; {len(m['hit_events'])} contact events. Status: NEEDS VISUAL SIGN-OFF.",f"![timing card]({name})",''])
(out/(character+'.md')).write_text('\n'.join(rows))
print(out)
