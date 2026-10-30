import pathlib, json, zipfile, io, math, hashlib, collections, re, csv, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT
SOURCE=ROOT/'original_sources'
CHARACTER_FILES={'T-elos':'T-elos','Ryu':'Ryu & Ken','Ken':'Ryu & Ken','Sheath':'Sheath','Saya':'Saya','Dante':'Dante & Vergil','Vergil':'Dante & Vergil','Captain Commando':'Captain Commando','Natsu':'Natsu','Juri Han':'Juri Han'}
char_dirs={}
for name in CHARACTER_FILES:
 c=name.lower().replace(' ','_').replace('-','_')
 d=OUT/'characters'/c
 (d/'frames').mkdir(parents=True,exist_ok=True)
 char_dirs[name]=d

archives=[]
records={c:[] for c in CHARACTER_FILES}
all_rows={c:[] for c in CHARACTER_FILES}

def cvbbox(mask):
 y,x=np.where(mask)
 if not len(x): return None
 return [int(x.min()),int(y.min()),int(x.max()),int(y.max())]

def row_grids(a):
 h,w=a.shape[:2]
 black=(a[:,:,:3].max(axis=2)<35)|(a[:,:,3]<20)
 blackrows=black.mean(axis=1)
 ys=np.where(blackrows>.83)[0]
 lines=[]
 if len(ys):
  s=old=int(ys[0])
  for y in ys[1:]:
   y=int(y)
   if y>old+1: lines.append((s,old));s=y
   old=y
  lines.append((s,old))
 bands=[];last=0
 for s,e in lines:
  if s-last>=34:bands.append((last,s-1))
  last=e+1
 if h-last>=34:bands.append((last,h-1))
 grids=[]
 for y0,y1 in bands:
  if y1-y0>310:continue
  g=black[y0:y1+1]
  col=np.where(g.mean(axis=0)>.87)[0]
  seq=[]
  if len(col):
   s=old=int(col[0])
   for x in col[1:]:
    x=int(x)
    if x>old+1:seq.append((s,old));s=x
    old=x
   seq.append((s,old))
  # strict repeated separators (at least 5) excluding far trailing black background
  sep=[]
  for s,e in seq:
   if e-s>8 and s>0:continue
   if sep and s-sep[-1][0]<25:continue
   sep.append((s,e))
  if len(sep)<7: continue
  # find dominant interval among separators; ignore off grid lines
  delta=np.diff([s for s,e in sep]); freq=collections.Counter([int(d) for d in delta if 65<=d<=280])
  if not freq:continue
  step=freq.most_common(1)[0][0]
  if sum(abs(d-step)<=3 for d in delta)<5:continue
  # group equal steps; retain largest valid group
  groups=[];cur=[sep[0]]
  for i,d in enumerate(delta):
   if abs(int(d)-step)<=3: cur.append(sep[i+1])
   else:
    if len(cur)>=6:groups.append(cur)
    cur=[sep[i+1]]
  if len(cur)>=6:groups.append(cur)
  if not groups:continue
  main=max(groups,key=len)
  # ensure first line black at x=0 or if gap at start, line x=0 could have another odd placement
  frame_cells=[]
  for left,right in zip(main,main[1:]):
   x0=left[1]+1;x1=right[0]-1
   if x1-x0 < 35:continue
   frame_cells.append([x0,y0,x1,y1])
  grids.append({'row_y':[y0,y1],'step':step,'cells':frame_cells})
 return grids

def alpha_cleanup(crop):
 a=np.array(crop).copy()
 rgb=a[:,:,:3].astype(np.int16)
 # strong magenta key + more tolerant connected border flood
 hard=(rgb[:,:,0]>=237)&(rgb[:,:,2]>=228)&(rgb[:,:,1]<=72)
 soft=(rgb[:,:,0]>170)&(rgb[:,:,2]>170)&(rgb[:,:,1]<165)&((rgb[:,:,0]+rgb[:,:,2]-2*rgb[:,:,1])>150)
 # background near border: flood filled soft magenta via cv2 connected components
 n, labels=cv2.connectedComponents(soft.astype('uint8'),8)
 touches=np.unique(np.r_[labels[0,:],labels[-1,:],labels[:,0],labels[:,-1]])
 touches=touches[touches>0]
 background=hard|np.isin(labels,touches)
 a[background,3]=0
 a[a[:,:,3]==0,:3]=0
 # actual RGBA no resample or compositing
 return Image.fromarray(a,mode='RGBA')

def features(a):
 rgb=a[:,:,:3]
 al=a[:,:,3]>30
 # only visible nonblack for classification
 px=rgb[al]
 if len(px)==0:return {'white':0,'red':0,'blue':0,'warm':0,'pixels':0}
 px=px.astype(np.int16)
 hi=px.max(axis=1);lo=px.min(axis=1)
 white=((hi-lo<45)&(hi>135)).sum()
 red=((px[:,0]>px[:,1]+35)&(px[:,0]>px[:,2]+20)&(px[:,0]>80)).sum()
 blue=((px[:,2]>px[:,0]+22)&(px[:,2]>px[:,1]+10)&(px[:,2]>65)).sum()
 warm=((px[:,0]>px[:,1]+18)&(px[:,1]>px[:,2]+5)&(px[:,0]>100)).sum()
 return {'white':int(white),'red':int(red),'blue':int(blue),'warm':int(warm),'pixels':len(px)}

def subject_class(name,feat):
 if 'Ryu & Ken' in name:
  # Ryu light white gi, Ken red gi. compare white to red, also reds on headband
  s=feat['white'];t=feat['red'];
  if s>320:return 'Ryu', 'high'
  if t>120:return 'Ken', 'high'
  return ('Ryu' if s>120 else 'Ken'), 'low'
 if 'Dante & Vergil' in name:
  s=feat['red'];t=feat['blue']
  if s>t*1.6 and s>25:return 'Dante','medium'
  if t>s*1.3 and t>25:return 'Vergil','medium'
  return ('Dante' if s>=t else 'Vergil'), 'low'
 for c in ('T-elos','Sheath','Saya','Captain Commando','Natsu','Juri Han'):
  if c in name:return c,'high'
 raise ValueError(name)

for p in sorted(SOURCE.glob('*.png')):
 raw=p.read_bytes()
 im=Image.open(io.BytesIO(raw)).convert('RGBA')
 a=np.array(im)
 grids=row_grids(a)
 print(p.name,im.size,'GRID_ROWS',len(grids),'cells',sum(len(g['cells']) for g in grids))
 archives.append({'filename':p.name,'dimensions':list(im.size),'sha256':hashlib.sha256(raw).hexdigest(),'grid_rows_detected':len(grids)})
 # preserve source in separate folder -- lossless
 (OUT/'original_sources').mkdir(exist_ok=True)
 (OUT/'original_sources'/p.name).write_bytes(raw)
 source_slug=('dante_vergil' if 'Dante & Vergil' in p.name else 'ryu_ken' if 'Ryu & Ken' in p.name else re.sub(r'[^a-z0-9]+','_',p.stem.lower()).strip('_')[-25:])
 for rownum,g in enumerate(grids,1):
  row_entries=[]
  for colnum,bbox in enumerate(g['cells'],1):
   x0,y0,x1,y1=bbox
   fr=alpha_cleanup(im.crop((x0,y0,x1+1,y1+1)))
   ra=np.array(fr)
   al=ra[:,:,3]>0
   # restrict to substantial assembled poses not isolated debris
   bb=cvbbox(al)
   if bb is None:continue
   ow=bb[2]-bb[0]+1;oh=bb[3]-bb[1]+1
   visible=int(al.sum())
   if visible<100 or oh<(y1-y0+1)*0.30 or ow<12: continue
   ft=features(ra)
   c,conf=subject_class(p.name,ft)
   if c not in char_dirs:continue
   id=f'{source_slug}_r{rownum:03d}_c{colnum:02d}'
   d=char_dirs[c]
   fp=d/'frames'/f'{id}.png'
   fr.save(fp)
   rec={'id':id,'png':f'frames/{id}.png','source_file':p.name,'crop_xyxy_inclusive':bbox,'grid_row':rownum,'grid_column':colnum,'canvas_size':list(fr.size),'bbox_inside_canvas':bb,'visible_pixels':visible,'speaker':None,'character_assignment_confidence':conf,'classification_features':ft,'foot_anchor_norm':[0.5,0.94]}
   records[c].append(rec)
   row_entries.append((colnum,c,rec))
  # per char row sequences, split by contiguous column and character (no implicit ordered animation guarantee)
  for c in char_dirs:
   subset=[(col,rec) for col,who,rec in row_entries if who==c]
   # preserve entire row and break at gaps
   groups=[];cur=[]
   for col,rec in subset:
    if cur and col>cur[-1][0]+1:
     groups.append(cur);cur=[]
    cur.append((col,rec))
   if cur:groups.append(cur)
   for group_idx,group in enumerate(groups,1):
    if len(group)<3:continue
    all_rows[c].append({'id':f'{source_slug}_row{rownum:03d}_take{group_idx}','frames':[v['png'] for _,v in group], 'source_columns':[k for k,_ in group], 'source_row':rownum,'frame_order_confidence':'provisional-sheet-order','preview_fps':10,'loop':False,'notes':'Original atlas order only. Not verified against PXZ2 gameplay. Inspect before animation binding.'})

# root content manifests
for c,d in char_dirs.items():
 rows=all_rows[c]
 data={'character':c,'source_game':'Project X Zone 2','source_original_archive':'Project x Zone 2 - 10 character Sprite pack.zip','count_assembled_poses':len(records[c]),'count_candidate_sequences':len(rows), 'state':'asset-import-candidate-not-runtime-verified','coordinate_convention':'0-based pixel x0/y0/x1/y1 inclusive','images':records[c], 'animations':rows, 'default_animation':'static_idle_placeholder','import_notes':['Use nearest pixel filtering. Use common canvas and explicit pivot for final runtime sequences.','Animation order/duration not embedded in PNG; groups provisional and must be reviewed.','Shared-sheet character identification uses color scoring. Review medium/low-confidence assignments.','Original source PNG retained separately and unchanged.']}
 (d/'manifest.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 # contact sheet of first frame of each candidate group, max 36 for overview
 contact_rows=rows[:36] if rows else []
 W=960;rowH=100
 preview=Image.new('RGB',(W,max(150,len(contact_rows)*rowH)),'#141921');draw=ImageDraw.Draw(preview)
 for i,r in enumerate(contact_rows):
  yy=i*rowH;path=d/r['frames'][0];fr=Image.open(path).convert('RGBA');fr.thumbnail((96,88),Image.Resampling.NEAREST)
  preview.paste(fr,(8,yy+4),fr)
  label=f'{r["id"]}  ·  {len(r["frames"])} frames  · provisional'
  draw.text((120,yy+30),label,fill='#f1f5ff')
  draw.line((0,yy+99,W,yy+99),fill='#344055')
 preview.save(d/'contact_sheet.png')
 print('  ',c,'frames',len(records[c]),'groups',len(rows),'low_conf',sum(x['character_assignment_confidence']=='low' for x in records[c]))

(OUT/'source_manifest.json').write_text(json.dumps({'sources':archives,'character_exports':{c:{'frames':len(records[c]),'sequences':len(all_rows[c]),'path':'characters/'+d.name+'/manifest.json'} for c,d in char_dirs.items()}},indent=2))
print('ROOT',OUT)
