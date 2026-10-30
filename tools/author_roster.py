"""Editable prototype recipes. Extract only explicitly listed assembled cells.
This does not infer native playback order or manufacture missing hand-drawn frames.
Usage: python tools/author_roster.py B3 | B | C | D
"""
from pathlib import Path
from PIL import Image
from scipy.ndimage import binary_propagation
import numpy as np,json,sys
R=Path(__file__).resolve().parents[1];stage=sys.argv[1] if len(sys.argv)>1 else 'D'
D=json.loads((R/'moves/choreography.json').read_text());MP=R/'assets/characters/roster_manifest.json'
manifest=json.loads(MP.read_text()) if MP.exists() else {'status':'Provisional authored order and timing, inspected assembled poses; original PNGs preserved.','frames':{}}
cache={}
def pose(cid,token):
 ident,t=token.split(':');face=-1
 if ident.endswith('+'):face=1;ident=ident[:-1]
 if cid in ['chunli','xiaoyu']:
  y,c=map(int,ident.split('.'));box=[2+c*120,y,120+c*120,y+118];offset=[69,66];anchor=[128,158 if cid=='xiaoyu' and y==1805 and c>=8 else 176];src='assist_source/ChunLi_Xiaoyu_original.png'
 else:
  block,row,c=ident.split('.');row=int(row);c=int(c)
  src='roster_source/Morrigan_original.png' if cid=='morrigan' else 'roster_source/Reiji_Xiaomu_original.png'
  if block=='d':box=[2+215*c,2515+162*row,215+215*c,2675+162*row];offset=[20,16];anchor=[128,158 if cid=='reiji' else 166]
  elif block=='g':
   y=[4135,4294,4451,4608][row];box=[2+162*c,y,162+162*c,y+155];offset=[47,15];anchor=[128,161]
  elif block=='i':box=[1+c*60,1,60+c*60,109];offset=[98,68];anchor=[128,176]
  elif block=='k':box=[2+c*116,112+row*140,116+c*116,251+row*140];offset=[70,36];anchor=[128,176]
  elif block=='b':box=[1+c*85,537,85+c*85,678];offset=[86,35];anchor=[128,176]
  else:raise ValueError(block)
 if src not in cache:cache[src]=Image.open(R/'assets/characters'/src).convert('RGBA')
 a=np.array(cache[src].crop(box));rgb=a[:,:,:3].astype(int)
 if cid=='morrigan':
  # Exact sheet greens/blue, not dark green hair or purple costume pixels.
  a[np.all(rgb==[0,255,80],2)|np.all(rgb==np.array(cache[src])[10,1499,:3],2),3]=0
 else:
  near=np.max(abs(rgb-[255,0,255]),2)<=24;seed=np.zeros(near.shape,bool);seed[0]=near[0];seed[-1]=near[-1];seed[:,0]=near[:,0];seed[:,-1]=near[:,-1]
  a[binary_propagation(seed,mask=near)|np.all(rgb==[255,0,255],2),3]=0
 # Grid separators only: never remove black contours within the artwork.
 black=rgb.max(2)<35
 for y in range(a.shape[0]):
  if black[y].mean()>.92:a[y,:,3]=0
 for x in range(a.shape[1]):
  if black[:,x].mean()>.92:a[:,x,3]=0
 out=R/f'assets/characters/{cid}/frames/{ident.replace(".","_")}.png';out.parent.mkdir(parents=True,exist_ok=True)
 canvas=Image.new('RGBA',(256,196));canvas.alpha_composite(Image.fromarray(a),tuple(offset));canvas.save(out)
 p={'path':'res://'+str(out.relative_to(R)),'ticks':int(t),'anchor':anchor,'native_facing':face,'attack_direction':face,'offset':[0,0],'source_rectangle':box,'canvas_offset':offset,'source_sheet':'assets/characters/'+src,'anchors':{},'mapping_status':'Provisional authored order; inspected assembled character pose.'}
 manifest['frames'][cid+'/'+ident]=p.copy();return p

def make(cid,key,title,frames,hits,distance=80,category='normal',role='main',cost=0,motion=None,cinema=None):
 poses=[pose(cid,x) for x in frames.split()];starts=[];duration=0
 for p in poses:starts.append(duration);duration+=p['ticks']
 events=[]
 for i,h in enumerate(hits):
  pi,box,reaction=h[:3];kind=h[3] if len(h)>3 else 'melee'
  profile={'up':'launcher','down':'finisher','right':'heavy'}.get(reaction,'energy' if kind=='projectile' else 'light')
  e={'id':f'{cid}_{key}_{i}','tick':starts[pi]+1,'end_tick':starts[pi]+3,'kind':kind,'damage':10 if category=='normal' else 15,'hitstun':42,'launch':280 if reaction=='up' else 90 if reaction=='left' else 0,'reaction':{'up':'rescue','down':'finish','left':'sustain'}.get(reaction,'ground'),'knockback':0,'xp':6 if category=='normal' else 0,'impact_profile':f'res://impacts/{profile}.tres','reaction_profile':'res://reactions/'+{'up':'vertical_launch','down':'downward_finish','right':'wall_drive'}.get(reaction,'light_stagger')+'.tres'}
  if kind=='melee':e['region']=box
  else:
   e.update(origin=box,origin_anchor='muzzle',speed=1250,flight_ticks=40,aim_snapshot=True,visual={'xiaomu':'seal','morrigan':'orb'}.get(cid,'bullet'),color={'xiaomu':'#ffe195','morrigan':'#bf88f4'}.get(cid,'#ffab69'))
   p=poses[pi];anchor=p['anchor'];p['anchors']['muzzle']=[anchor[0]+box[0]/1.7/p['native_facing'],anchor[1]+box[1]/1.7]
   if cid=='xiaomu':e.update(aim_snapshot=False,aim_angle=-.18)
  if reaction=='right':e.update(horizontal_speed=300,wall_bounce=True)
  if category=='ultimate':e.update(damage=18 if i<len(hits)-1 else 65,capture=i==0,ultimate_finish=i==len(hits)-1,impact_profile='res://impacts/ultimate.tres' if i==len(hits)-1 else e['impact_profile'])
  events.append(e)
 m={'sequence_id':cid+'_'+key,'display_name':title+' / prototype','character':cid,'role':role,'category':category,'purpose':key,'duration_ticks':duration,'poses':poses,'hit_events':events,'movement':motion or [],'cues':[{'tick':4,'effect':'trail'},{'tick':1,'sound_event':'ultimate' if category=='ultimate' else 'special' if category=='special' else 'assist' if role=='assist' else 'attack'}],'chain_open':duration-15,'chain_close':duration-1,'cancel_open':12,'cancel_close':duration-20,'resource_cost':cost,'staging':{'distance':distance,'entry_offset':145,'approach_start':2,'approach_end':15,'commit_tick':12,'exit_start':duration-14,'exit_end':duration,'max_correction':650 if role=='assist' else 850,'alignment_limit':22,'height_ratio':.85,'max_elevation':140},'cinematic_spec':cinema or {}}
 if cid=='xiaomu' and role=='assist':m['staging'].update(height_ratio=.3,max_elevation=50)
 if cid=='xiaomu' and role=='main' and all(e.get('kind')=='projectile' for e in events):m['staging'].update(height_ratio=0,max_elevation=0)
 if category=='ultimate':
  m.update(chain_open=duration+1,chain_close=duration+1,cancel_open=duration+1,cancel_close=duration+1)
  m['cinematic_spec'].update(title=title,miss_gate=events[0]['end_tick']+35,release_tick=events[-1]['end_tick']+20,duration=duration,presentation='martial')
  m['cinematic_spec'].setdefault('capture_height',35)
 D['moves']=[x for x in D['moves'] if x['sequence_id']!=m['sequence_id']]+[m]
 return m

def hit(pi,box,role='ground',kind='melee'):return (pi,box,role,kind)
# Coordinates are local, narrow limb/weapon contact regions, not arena-wide boxes.
ck=[75,-108,38,30];ch=[45,-161,42,35];xp=[25,-112,34,30];xh=[38,-169,32,32]
if stage in ['B3','B','D']:
 C='chunli'
 make(C,'neutral','Blue Rhythm','1685.0:16 1685.1:8 1685.2:6 1685.3:6 1685.4:10 1685.8:10 1685.9:18',[hit(1,[44,-130,35,32]),hit(4,[50,-110,40,34])],86)
 make(C,'left','Silk Leg Cadence','1685.2:16 1685.3:5 1685.4:5 1685.5:5 1685.6:6 1685.7:7 1685.8:8 1685.9:18',[hit(2,ck,'left'),hit(3,ck,'left'),hit(4,ch,'left'),hit(5,ck,'left')],105)
 make(C,'down','Turning Heel','1685.10:15 1685.11:7 1685.12:6 1685.13:10 1685.14:8 1685.15:10 1685.9:18',[hit(3,[15,-177,44,40]),hit(4,[28,-142,44,42],'down')],70)
 C='xiaoyu'
 make(C,'neutral','Twin Palm Flow','1925.7:16 1925.0:9 1925.1:8 1925.2:7 1925.3:9 1925.6:10 1925.7:18',[hit(1,[30,-110,37,36]),hit(4,[25,-105,37,36])],63)
 make(C,'left','Turning Circle','1445.8:16 1445.9:8 1445.10:8 1445.11:6 1445.12:8 1445.13:8 1445.14:10 1445.15:18',[hit(i,[25,-125,38,36],'left') for i in [2,4,5]],65)
 make(C,'down','Low Wing Sweep','1805.0:16 1805.1:8 1805.2:9 1805.6:8 1805.7:8 1805.8:8 1805.9:10 1805.10:8 1445.7:20',[hit(2,[35,-52,40,36]),hit(6,[40,-21,42,35],'down')],72)
if stage in ['B','D']:
 C='chunli'
 make(C,'up','Sky Step','1925.8:16 1925.9:5 1925.10:5 1925.11:7 1925.12:7 1925.13:10 2045.0:8 2045.1:8 2045.2:18',[hit(3,[30,-110,40,35]),hit(5,[30,-159,40,40],'up')],67)
 make(C,'right','Driving Split','1565.12:16 1565.13:8 1565.14:10 1565.15:10 1685.0:8 1685.1:8 1685.9:18',[hit(1,[65,-100,43,35]),hit(2,[65,-100,43,35]),hit(5,[44,-130,35,32],'right')],96)
 make(C,'special_1','Hundred-Petal Burst','1685.2:18 1685.3:6 1685.4:5 1685.5:5 1685.6:5 1685.7:5 1685.4:5 1685.5:5 1685.6:8 1685.8:8 1685.9:20',[hit(i,ch if i in [4,8] else ck,'left') for i in [2,3,4,5,6,7,8]],100,'special',cost=90)
 make(C,'special_2','Rising Lotus','1925.8:18 1925.10:8 1925.11:8 1925.12:8 1925.13:10 2045.0:12 2045.1:12 2045.2:20',[hit(2,[28,-108,42,35]),hit(4,[30,-160,42,42],'up'),hit(5,[30,-150,45,40],'left')],70,'special',cost=120,motion=[{'tick':0,'x':0,'y':0},{'tick':32,'x':0,'y':0},{'tick':50,'x':0,'y':-38},{'tick':72,'x':0,'y':0}])
 make(C,'ultimate','Azure Spiral Finale','1685.2:30 1685.3:20 1685.4:12 1685.5:12 1685.6:10 1685.7:10 1925.11:15 1925.12:12 1925.13:14 2045.0:14 2045.1:16 1685.13:20 1685.14:12 1685.15:20 1685.9:35',[hit(i,[50,-132,48,42] if i<6 else [20,-158,48,50]) for i in [2,3,4,5,8,9,11]]+[hit(12,[25,-142,48,44],'down')],80,'ultimate',cost=300,cinema={'motif':'spiral','stages':[{'tick':0,'name':'CONFIRM'},{'tick':30,'name':'COILED STANCE'},{'tick':50,'name':'RAPID KICK FAN'},{'tick':110,'name':'ASCENDING SPIRAL'},{'tick':205,'name':'HEEL DESCENT'},{'tick':235,'name':'AFTERMATH'}]})
 C='xiaoyu'
 make(C,'up','Phoenix Rise','1445.2:16 1445.3:9 1445.4:7 1445.5:9 1445.6:10 1445.7:18',[hit(1,xp),hit(3,xh,'up')],61)
 make(C,'right','Wheel Turn','1565.0:16 1565.1:7 1565.2:7 1565.3+:7 1565.4+:8 1565.5+:8 1565.6+:8 1565.7:8 1565.8:8 1565.9:8 1565.10:8 1565.11:18',[hit(4,[40,-124,42,35]),hit(6,[38,-118,42,35]),hit(10,[35,-110,40,35],'right')],76)
 make(C,'special_1','Double-Palm Echo','1925.7:18 1925.0:9 1925.1:6 1925.2:7 1925.3:9 1925.4:6 1925.5:9 1925.6:10 1925.7:20',[hit(i,[30,-112,40,38]) for i in [1,4,6]],64,'special',cost=90)
 make(C,'special_2','Phoenix Rescue','1445.2:16 1445.3:9 1445.4:7 1445.5:10 1445.6:10 1445.7:8 1445.8:10 1445.9:10 1445.10:10 1445.15:20',[hit(1,xp),hit(3,xh,'up'),hit(8,[25,-125,38,36],'left')],61,'special',cost=120)
 make(C,'ultimate','Phoenix Orbit','1445.8:28 1445.9:20 1445.10:14 1445.11:12 1445.12:14 1445.13:12 1565.2:14 1565.3+:12 1565.4+:14 1565.5+:12 1565.6+:14 1445.3:12 1445.5:16 1805.7:14 1805.8:12 1805.9:14 1805.10:16 1445.7:36',[hit(2,[25,-125,40,38]),hit(4,[25,-125,40,38]),hit(8,[40,-125,42,40]),hit(10,[40,-120,42,40]),hit(12,xh),hit(15,[40,-21,42,35],'down')],65,'ultimate',cost=300,cinema={'motif':'orbit','capture_height':0,'stages':[{'tick':0,'name':'CONFIRM'},{'tick':28,'name':'TURNING STANCE'},{'tick':48,'name':'PALM CIRCLE'},{'tick':114,'name':'WHEEL REVERSAL'},{'tick':228,'name':'LOW WING FINISH'},{'tick':260,'name':'AFTERMATH'}]})
sword=[45,-86,55,42];thrust=[65,-96,55,38];palm=[20,-108,36,35]
if stage in ['C','D']:
 make('reiji','neutral','Twin Steel Draw','d.4.5:16 d.4.8:8 d.5.2:8 d.5.5:10 d.6.6:8 d.6.8:10 d.9.3:20',[hit(3,sword),hit(5,thrust)],105)
 make('reiji','assist','Cross-Draw Support','d.4.8:16 d.5.5:9 d.6.6:8 d.6.8:10 d.9.3:18',[hit(1,sword,'left'),hit(3,thrust,'left')],104,role='assist')
 make('xiaomu','neutral','Fox Step','d.1.0:16 d.1.1:7 d.1.2:9 d.1.3:8 d.2.4:8 d.3.1:10 d.3.6:20',[hit(3,palm),hit(5,[25,-104,40,36])],55)
 make('xiaomu','assist','Foxfire Cover','g.0.1:16 g.0.7:8 g.0.8:8 g.0.9:8 g.0.10:9 g.0.11:8 g.0.5:20',[hit(2,[90,-158],'left','projectile'),hit(4,[90,-158],'up','projectile')],170,role='assist')
 make('morrigan','neutral','Velvet Turn','k.0.0:16 k.0.1:8 k.0.2:7 k.0.3+:9 k.0.4:8 k.0.5:10 k.0.9:8 k.0.10:18',[hit(3,[30,-129,45,38]),hit(5,[45,-100,45,40])],80)
 make('morrigan','assist','Night Wing','b.0.2:16 b.0.3:8 b.0.4:7 b.0.5:8 b.0.6:9 b.0.7:8 b.0.8:10 b.0.10:20',[hit(3,[22,-120,42,40],'left'),hit(6,[15,-180,40,50],'up')],62,role='assist')
if stage=='D':
 C='reiji'
 make(C,'left','Covering Steel','d.9.3:16 d.7.0:8 d.7.1:8 d.7.2:8 d.7.0:8 d.7.1:9 d.9.3:20',[hit(1,[102,-89],'left','projectile'),hit(4,[102,-89],'left','projectile')],215)
 make(C,'up','Rising Draw','d.4.5:16 d.5.0:8 d.5.5:8 d.5.6:9 d.6.0:10 d.6.3:9 d.9.3:20',[hit(2,sword),hit(4,[15,-181,55,60],'up')],80)
 make(C,'down','Severing Arc','d.6.6:18 d.6.8:10 d.6.0:9 d.5.6:10 d.5.5:12 d.9.0:10 d.9.3:20',[hit(1,thrust),hit(4,sword,'down')],100)
 make(C,'right','Steel Pursuit','d.7.7:16 d.7.8:8 d.7.9:8 d.8.0:8 d.8.1:8 d.8.2:10 d.9.3:20',[hit(3,[60,-108,60,38]),hit(5,thrust,'right')],108)
 make(C,'special_1','Gunmetal Salvo','d.9.3:18 d.7.0:8 d.7.1:8 d.7.0:8 d.7.1:8 d.7.2:9 d.9.1:8 d.9.3:22',[hit(i,[102,-89],'ground','projectile') for i in [1,2,3,4]],225,'special',cost=90)
 make(C,'special_2','Guard-Break Ascent','d.4.8:18 d.5.2:8 d.5.5:10 d.6.0:10 d.6.3:8 d.6.8:10 d.9.3:22',[hit(2,sword),hit(3,[15,-181,55,60],'up'),hit(5,thrust,'left')],80,'special',cost=120,motion=[{'tick':0,'x':0,'y':0},{'tick':38,'x':0,'y':0},{'tick':55,'x':0,'y':-40},{'tick':78,'x':0,'y':0}])
 m=make(C,'ultimate','Crimson Arsenal','d.9.3:28 d.7.7:20 d.7.0:14 d.7.1:14 d.7.2:14 d.4.8:25 d.5.0:16 d.5.5:14 d.6.8:16 d.6.0:20 d.5.5:18 d.6.8:18 d.9.0:22 d.9.3:40',[hit(2,[102,-89],'ground','projectile'),hit(3,[102,-89],'ground','projectile'),hit(7,sword),hit(8,thrust),hit(10,sword),hit(11,thrust,'down')],235,'ultimate',cost=300,cinema={'motif':'cross_slash','stages':[{'tick':0,'name':'CONFIRM'},{'tick':28,'name':'GUN DRAW'},{'tick':48,'name':'COVERING VOLLEY'},{'tick':90,'name':'STEEL APPROACH'},{'tick':131,'name':'CROSSING BLADES'},{'tick':201,'name':'SEVERING FINISH'},{'tick':240,'name':'AFTERMATH'}]})
 m['staging']['segments']=[{'tick':91,'distance':100,'approach_ticks':24,'height_ratio':.65}]
 C='xiaomu'
 make(C,'left','Foxfire Fan','g.0.1:16 g.0.7:8 g.0.8:8 g.0.9:7 g.0.10:9 g.0.11:8 g.0.5:20',[hit(2,[90,-158],'left','projectile'),hit(4,[90,-158],'left','projectile')],170)
 make(C,'up','Fox Tail Rise','d.1.0:16 d.1.1:8 d.2.4:8 d.2.5:8 d.3.1:9 d.2.7:8 d.3.0:10 d.3.6:20',[hit(2,[25,-103,35,36]),hit(4,[25,-130,40,40],'up')],55)
 make(C,'down','Crescent Landing','d.2.4:16 d.2.6:9 d.3.0:8 d.3.1:8 d.3.2:9 d.3.3:9 d.3.4:10 d.3.6:20',[hit(2,[30,-115,42,40]),hit(5,[25,-84,42,40],'down')],60)
 make(C,'right','Fox Chase','g.1.0:16 g.1.1:9 g.1.2:8 g.1.3:9 g.1.4:8 g.1.5:9 g.1.11:20',[hit(1,[58,-102],'ground','projectile'),hit(4,[90,-158],'right','projectile')],160)
 make(C,'special_1','Golden Fan Volley','g.0.1:18 g.0.7:8 g.0.8:8 g.0.9:8 g.0.10:8 g.0.11:8 g.2.0:8 g.2.1:8 g.0.5:22',[hit(i,[90,-158],'ground','projectile') for i in [2,3,4,5]],170,'special',cost=90)
 make(C,'special_2','Foxfire Lift','g.0.1:18 g.0.7:8 g.0.8:10 g.0.9:9 g.0.10:10 g.0.11:10 g.0.5:24',[hit(2,[90,-158],'up','projectile'),hit(4,[90,-158],'left','projectile')],170,'special',cost=120)
 make(C,'ultimate','Golden Fox Procession','d.0.0:28 d.0.2:18 d.0.3:16 g.0.7:20 g.0.8:16 g.0.9:15 g.0.10:17 g.1.4:17 g.1.5:19 g.2.0:20 g.2.1:18 g.0.11:25 g.0.5:42',[hit(i,[90,-158],'down' if i==11 else 'ground','projectile') for i in [4,5,6,7,8,10,11]],170,'ultimate',cost=300,cinema={'motif':'foxfire','stages':[{'tick':0,'name':'CONFIRM'},{'tick':28,'name':'STAFF INVOCATION'},{'tick':62,'name':'DUAL GUN DRAW'},{'tick':82,'name':'SEAL PROCESSION'},{'tick':186,'name':'GOLDEN FAN'},{'tick':229,'name':'AFTERMATH'}]})
 C='morrigan'
 make(C,'left','Night Orb','k.0.0:16 k.0.1:10 k.0.0:8 k.0.1:10 k.0.10:20',[hit(1,[43,-118],'left','projectile'),hit(3,[43,-118],'left','projectile')],170)
 make(C,'up','Rising Wing Blade','b.0.2:16 b.0.3:8 b.0.4:8 b.0.5:8 b.0.6:8 b.0.7:8 b.0.8:10 b.0.9:10 b.0.10:20',[hit(3,[22,-120,42,40]),hit(6,[15,-180,40,50],'up')],62)
 make(C,'down','Velvet Descent','k.1.6:16 k.1.7:9 k.1.8:9 k.1.9:9 k.1.10:10 k.1.11:10 k.0.9:10 k.0.10:20',[hit(2,[25,-85,48,42]),hit(4,[35,-100,48,42],'down')],74)
 make(C,'right','Batwing Drive','k.0.1:16 k.0.2:8 k.0.3+:8 k.0.4:8 k.0.5:8 k.0.6:8 k.0.7:9 k.0.9:10 k.0.10:20',[hit(2,[30,-129,45,38]),hit(4,[45,-100,45,40]),hit(6,[25,-125,45,40],'right')],78)
 make(C,'special_1','Violet Soul Volley','k.0.0:18 k.0.1:9 k.0.0:7 k.0.1:9 k.0.0:7 k.0.1:10 k.0.10:24',[hit(i,[43,-118],'ground','projectile') for i in [1,3,5]],190,'special',cost=90)
 make(C,'special_2','Nightwing Rescue','b.0.2:18 b.0.3:8 b.0.5:9 b.0.6:9 b.0.7:9 b.0.8:10 b.0.9:10 b.0.10:24',[hit(2,[22,-120,42,40]),hit(5,[15,-180,40,50],'up')],62,'special',cost=120)
 make(C,'ultimate','Nightfall Masquerade','i.0.0:30 b.0.2:18 b.0.3:16 b.0.4:14 b.0.5:14 b.0.6:14 b.0.7:16 b.0.8:18 b.0.9:18 k.1.6:20 k.1.7:18 k.1.8:16 k.1.9:16 k.1.10:18 k.0.9:18 k.0.10:40',[hit(4,[22,-120,42,40]),hit(6,[20,-170,40,50]),hit(7,[15,-180,40,50]),hit(10,[30,-100,48,44]),hit(11,[25,-85,48,42]),hit(13,[35,-100,48,42],'down')],68,'ultimate',cost=300,cinema={'motif':'nightfall','stages':[{'tick':0,'name':'CONFIRM'},{'tick':30,'name':'WING METAMORPHOSIS'},{'tick':78,'name':'SHADOW ASCENT'},{'tick':158,'name':'VELVET DIVE'},{'tick':228,'name':'NIGHTFALL FINISH'},{'tick':264,'name':'AFTERMATH'}]})
exec((R/'tools/save_packages.py').read_text())
