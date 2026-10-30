from pathlib import Path
import json,hashlib
from PIL import Image, ImageDraw
import numpy as np
from scipy.ndimage import binary_propagation
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'assets/characters/assist_source/ChunLi_Xiaoyu_original.png'
im=Image.open(source).convert('RGBA')
manifest={'source':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'dimensions':list(im.size),'format':'PNG RGBA; no JPEG compression observed','method':'Edge-connected near-magenta (max difference 24) plus exact magenta only; no removal of black or non-background purple/pink. Assembled poses only.','notes':'Character identification visually reviewed: Chun-Li blue outfit/buns; Xiaoyu orange outfit/pigtails. Frame order and durations authored provisionally, not verified native animation order.','canvas':[256,196],'pivot':[128,176],'characters':{}}
# Explicit source rectangles, no assumption of one atlas-wide cell size.
specs={'chunli':{'idle':[818,1344,884,1441],'row':1685,'columns':[2,3,4,5,6,7,8,9],'ticks':[14,10,6,6,6,8,10,15]},'xiaoyu':{'idle':[2,1344,68,1441],'row':1445,'columns':[2,3,4,5,6,7],'ticks':[18,12,12,6,12,25]}}
preview=Image.new('RGB',(1024,520),(21,33,49));draw=ImageDraw.Draw(preview)
for row,(cid,spec) in enumerate(specs.items()):
 frames=[]; folder=ROOT/'assets/characters'/cid/'frames';folder.mkdir(parents=True,exist_ok=True)
 rectangles=[spec['idle']]+[[2+c*120,spec['row'],120+c*120,spec['row']+118] for c in spec['columns']]
 for index,box in enumerate(rectangles):
  crop=np.array(im.crop(box));rgb=crop[:,:,:3].astype(int)
  near=(np.abs(rgb-np.array([255,0,255])).max(axis=2)<=24)
  seed=np.zeros(near.shape,bool);seed[0,:]=near[0,:];seed[-1,:]=near[-1,:];seed[:,0]=near[:,0];seed[:,-1]=near[:,-1]
  remove=binary_propagation(seed,mask=near)|np.all(rgb==[255,0,255],axis=2)
  crop[remove,3]=0
  art=Image.fromarray(crop)
  offset=[128-art.width//2,81 if index==0 else 66]
  canvas=Image.new('RGBA',(256,196));canvas.alpha_composite(art,tuple(offset))
  name='idle' if index==0 else 'assist_%02d'%(index-1)
  output=folder/(name+'.png');canvas.save(output)
  frames.append({'path':'res://'+str(output.relative_to(ROOT)),'source_rectangle':box,'canvas_offset':offset,'offset':[0,0],'ticks':60 if index==0 else spec['ticks'][index-1]})
  if index>0:
   x=(index-1)*128;y=row*260
   show=canvas.crop((64,46,192,186));preview.paste(show,(x,y+35),show)
   draw.text((x+4,y+8),cid+' '+str(index-1),fill='white')
   draw.text((x+4,y+185),str(frames[-1]['ticks'])+' ticks',fill='#a8dfe8')
 manifest['characters'][cid]={'idle':frames[0],'assist':frames[1:]}
(ROOT/'assets/characters/assist_manifest.json').write_text(json.dumps(manifest,indent=2))
preview.save(ROOT/'docs/AssistPoseMapping.png')
choreo=json.loads((ROOT/'moves/choreography.json').read_text())
for move in choreo['moves']:
 if move['character'] in specs:
  move['poses']=manifest['characters'][move['character']]['assist']
  if move['character']=='xiaoyu':move['display_name']='Phoenix Lift / prototype'
choreo['status']='Checkpoint A: three correct character visuals, limited inspected pose selections. Choreography is prototype-authored; original frame timing not verified.'
(ROOT/'moves/choreography.json').write_text(json.dumps(choreo,indent=2))
print('Extracted 16 transparent assist/idle PNGs; original preserved.')
