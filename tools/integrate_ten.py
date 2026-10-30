"""Inspected prototype recipes. Tokens row.column[:source-facing].
Pivots are constant per source row. No per-frame opaque-bound centering.
Hit tuple: pose index, source contact x/y, type, reaction.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];K=R/'assets/import_kit';D=json.loads((R/'moves/choreography.json').read_text())
pivots={'t_elos':{1:[76,145],2:[76,145],3:[76,145]},'ryu':{2:[58,113],3:[58,113],9:[54,117],12:[58,118]},'ken':{1:[58,114],2:[58,114],6:[58,106]},'sheath':{1:[95,130],4:[85,134],6:[85,126]},'saya':{1:[76,143],3:[76,143]},'dante':{1:[38,107],6:[125,145],7:[125,145],18:[94,163],19:[94,171],14:[105,150]},'vergil':{1:[42,107],2:[135,156],4:[135,145],5:[135,145]},'captain_commando':{2:[80,129],1:[80,129],3:[80,126]},'natsu':{1:[67,126],2:[67,126],3:[67,126],4:[67,126],5:[67,126]},'juri_han':{1:[64,118],2:[64,118],3:[64,120]}}
recipes={
't_elos':('T-elos','1.1',1,'#d875f0',[
('Circuit Cleave','1.3 1.5 1.7 1.9 1.11 1.13 1.15',[(2,112,109,'melee','ground'),(5,121,101,'melee','sustain')]),
('Arm Emitter Volley','2.1 2.2 2.3 2.5 2.7 2.9 2.11',[(2,115,94,'projectile','sustain'),(4,115,94,'projectile','sustain')]),
('Descending Circuit','3.1 3.3 3.5:-1 3.7 3.8 3.11 3.15',[(2,39,92,'melee','ground'),(4,117,85,'melee','finish')])]),
'ryu':('Ryu','2.7',-1,'#b4e8ff',[
('Iron Rhythm','2.7 2.16 2.18 3.3 3.5 3.6 3.7',[(2,23,63,'melee','ground'),(4,23,73,'melee','sustain')]),
('Palm Wave Cadence','9.9 9.11 9.12 9.14 9.16 9.18',[(2,25,66,'projectile','sustain'),(4,25,66,'projectile','sustain')]),
('Driving Heel','12.2 12.5 12.7 12.10 12.12 12.15',[(2,44,34,'melee','ground'),(3,28,70,'melee','finish')])]),
'ken':('Ken','1.1',1,'#ff9b53',[
('Scarlet Rush','1.1 1.7 1.9 1.15 1.17 1.20 2.6',[(2,91,49,'melee','ground'),(4,99,49,'melee','sustain')]),
('Flame Step Rhythm','6.1 6.4 6.6:-1 6.9:-1 6.12 6.15 6.20',[(3,19,64,'melee','sustain'),(5,101,67,'melee','sustain')]),
('Falling Axe','2.1 2.2 2.3 2.4 2.5 2.6',[(1,81,30,'melee','ground'),(2,103,65,'melee','finish')])]),
'sheath':('Sheath','1.1',1,'#f6c86b',[
('Clockwork Edge','6.1 6.2 6.3 6.5 6.8 6.10 6.14',[(2,132,58,'melee','ground'),(5,120,72,'melee','sustain')]),
('Clockside Volley','4.4:-1 4.5:-1 4.7:-1 4.8:-1 4.10:-1 4.11:-1',[(3,38,48,'projectile','sustain'),(4,38,48,'projectile','sustain')]),
('Twin Edge Verdict','1.1 1.4:-1 1.6 1.8 1.10 1.11:-1 1.13:-1',[(2,133,73,'melee','ground'),(5,36,55,'melee','finish')])]),
'saya':('Saya','1.1',1,'#ff739f',[
('Fox Blade Pursuit','3.1 3.3 3.4 3.7 3.9:-1 3.11 3.13',[(2,103,79,'melee','ground'),(4,23,80,'melee','sustain')]),
('Crimson Cover','1.1 1.3 1.5 1.7 1.9 1.11',[(2,117,71,'projectile','sustain'),(3,117,71,'projectile','sustain')]),
('Low Blade Reversal','3.3 3.4 3.7 3.9:-1 3.13 3.15',[(1,103,79,'melee','ground'),(3,23,80,'melee','finish')])]),
'dante':('Dante','1.7',-1,'#ff855f',[
('Redline Thrust','6.2 6.3 6.4 6.5 6.7 6.8 7.1',[(3,56,76,'melee','ground'),(5,56,76,'melee','sustain')]),
('Armament Cover','14.9 14.2 14.1 14.3 14.7 14.8 14.9',[(2,43,87,'projectile','sustain'),(4,43,81,'projectile','sustain')]),
('Rebellion Fall','18.5 18.6 18.7 18.8:1 18.10 18.9 18.12',[(3,159,101,'melee','ground'),(5,64,125,'melee','finish')])]),
'vergil':('Vergil','1.1',-1,'#89c5ff',[
('Blue Draw','2.1 2.2 2.4 2.6 2.7 2.10',[(2,71,109,'melee','ground'),(4,70,109,'melee','sustain')]),
('Measured Steel','5.1 5.2 5.3 5.4 5.6 5.8 5.10',[(2,61,87,'melee','sustain'),(5,59,76,'melee','sustain')]),
('Yamato Descent','4.1 4.4 4.6 4.7 4.8 4.9 4.10',[(2,60,72,'melee','rescue'),(4,124,35,'melee','finish')])]),
'captain_commando':('Captain Commando','2.1',-1,'#7cddff',[
('Captain Combination','2.1 2.3 2.5 2.7 2.10 2.14 2.16',[(3,39,64,'melee','ground'),(5,28,83,'melee','sustain')]),
('Powered Fist Cadence','1.4 1.6 1.7 1.9 2.3 2.5 2.7',[(1,34,65,'melee','sustain'),(6,39,64,'melee','sustain')]),
('Ground Breaker','3.1 3.2 3.3 3.4 3.5',[(2,72,91,'melee','ground'),(3,64,119,'melee','finish')])]),
'natsu':('Natsu','1.1',-1,'#ffa490',[
('Scarlet Blade Run','3.6 3.8 3.10 3.12 3.15 4.10',[(1,37,77,'melee','ground'),(3,37,94,'melee','sustain')]),
('Crossed Steel','4.10 4.12 4.15 4.17 5.1',[(1,26,55,'melee','sustain'),(3,66,31,'melee','sustain')]),
('Blade Drop','1.10 1.12 1.15 2.1 2.3 3.3',[(1,27,59,'melee','ground'),(4,30,112,'melee','finish')])]),
'juri_han':('Juri Han','1.1',1,'#dc8bff',[
('Violet Hook','2.1 2.3 2.6 2.8 2.11 2.13 2.18',[(1,107,62,'melee','ground'),(4,105,83,'melee','sustain')]),
('Turning Fang','3.1 3.3 3.5 3.7 3.8 3.10 3.14',[(3,101,56,'melee','sustain'),(4,110,81,'melee','sustain')]),
('Falling Scythe','1.3 1.6 1.8 1.11 1.13 1.16 1.18',[(2,113,79,'melee','ground'),(5,91,42,'melee','finish')])])}
manifest={'status':'Inspected prototype mappings; unfinished slots unavailable','characters':{}}
for cid,(name,idle,face,palette,moves) in recipes.items():
 src=json.loads((K/'characters'/cid/'manifest.json').read_text());lookup={(i['grid_row'],i['grid_column']):i for i in src['images']}
 def pose(token,ticks=8):
  rc,*override=token.split(':');row,col=map(int,rc.split('.'));item=lookup[(row,col)]
  return {'path':f"res://assets/import_kit/characters/{cid}/{item['png']}",'ticks':ticks,'anchor':pivots[cid][row],'native_facing':int(override[0]) if override else face,'offset':[0,0],'source_rectangle':item['crop_xyxy_inclusive'],'source_sheet':item['source_file'],'mapping_status':'Prototype order and timing, not verified original move.'}
 authored=[]
 for slot,(title,tokens,hits) in zip(['neutral','left','down'],moves):
  poses=[pose(t) for t in tokens.split()];poses[0]['ticks']=16;poses[-1]['ticks']=16
  starts=[];t=0
  for p in poses:starts.append(t);t+=p['ticks']
  events=[];reach=[]
  for k,(idx,x,y,kind,reaction) in enumerate(hits):
   p=poses[idx];ax,ay=p['anchor'];lx=(x-ax)*1.7*p['native_facing'];ly=(y-ay)*1.7;reach.append(max(15,lx))
   e={'id':f'{cid}_{slot}_{k}','tick':starts[idx]+2,'end_tick':starts[idx]+4,'kind':kind,'damage':13 if k==0 else 19,'hitstun':45,'hitstop':3 if k==0 else 5,'launch':280 if reaction=='rescue' else 75 if reaction=='sustain' else 0,'knockback':0,'xp':7,'reaction':reaction,'impact_profile':'res://impacts/'+('finisher' if reaction=='finish' else 'energy' if kind=='projectile' else 'light')+'.tres'}
   if kind=='melee':e['region']=[lx-16,ly-19,32,38]
   else:p['anchors']={'muzzle':[x,y]};e.update(origin_anchor='muzzle',origin=[lx,ly],speed=1250,flight_ticks=35,aim_snapshot=False,visual='orb' if cid in ['ryu','t_elos'] else 'bullet',color=palette)
   events.append(e)
  dist=round(sum(reach)/len(reach))+18+(105 if events[0]['kind']=='projectile' else 0)
  m={'sequence_id':cid+'_'+slot,'display_name':title+' / prototype','character':cid,'role':'main','category':'normal','purpose':slot,'poses':poses,'duration_ticks':t,'hit_events':events,'movement':[],'cues':[{'tick':1,'sound_event':'attack'}],'chain_open':t-14,'chain_close':t-1,'cancel_open':12,'cancel_close':t-15,'staging':{'distance':dist,'entry_offset':130,'approach_start':2,'approach_end':14,'commit_tick':12,'exit_start':t-14,'exit_end':t,'max_correction':850,'alignment_limit':20,'height_ratio':.8,'max_elevation':130}}
  if all(e['kind']=='projectile' for e in events):m['staging'].update(height_ratio=0,max_elevation=0)
  if cid=='vergil' and slot=='down':m['staging']['segments']=[{'tick':starts[3],'distance':33,'approach_ticks':6,'height_ratio':0}]
  if cid=='natsu' and slot=='left':m['staging']['segments']=[{'tick':starts[2],'distance':24,'approach_ticks':6,'height_ratio':.8}]
  D['moves']=[x for x in D['moves'] if x['sequence_id']!=m['sequence_id']]+[m];authored.append(m)
 assist=json.loads(json.dumps(authored[1]));assist.update(sequence_id=cid+'_assist',display_name=authored[1]['display_name'].replace(' / prototype',' Support / prototype'),role='assist');assist['cues']=[{'tick':1,'sound_event':'assist'}];assist['staging']['max_correction']=650
 D['moves']=[x for x in D['moves'] if x['sequence_id']!=assist['sequence_id']]+[assist]
 still=pose(idle);base=[f'res://moves/{cid}_neutral.tres',f'res://moves/{cid}_left.tres','',f'res://moves/{cid}_down.tres','']
 vals={'character_id':cid,'display_name':name,'idle_texture':still['path'],'portrait_texture':still['path'],'native_facing':face,'main_sequences':base,'special_sequences':['',''],'ultimate_sequence':'','assist_sequence':f'res://moves/{cid}_assist.tres','assist_variants':[f'res://moves/{cid}_assist.tres'],'supported_roles':['main','assist'],'completion_status':'partial / 3 normals + assist','availability_note':'J / Left+J / Down+J and assist authored. Up/Right, specials, ultimate unavailable. No confirmed voices.','source_manifest':f'res://assets/import_kit/characters/{cid}/manifest.json','artwork_status':'Supplied assembled poses / provisional choreography'}
 lines=['[gd_resource type="Resource" script_class="CharacterDefinition" load_steps=3 format=3]','[ext_resource type="Script" path="res://battle/CharacterDefinition.gd" id="1"]',f'[ext_resource type="Resource" path="res://sounds/{cid}.tres" id="voice"]','[resource]','script = ExtResource("1")','sound_profile = ExtResource("voice")']
 for key,val in vals.items():lines.append(key+' = '+('Array[String]('+json.dumps(val)+')' if isinstance(val,list) else json.dumps(val)))
 lines+=['pivot = Vector2('+','.join(map(str,still['anchor']))+')','effect_palette = Color('+','.join(str(int(palette[i:i+2],16)/255) for i in (1,3,5))+',1)','portrait_region = Rect2(0,0,'+','.join(map(str,lookup[tuple(map(int,idle.split('.')))]['canvas_size']))+')']
 (R/f'moves/{cid}.tres').write_text('\n'.join(lines)+'\n');(R/f'sounds/{cid}.tres').write_text((R/'sounds/reiji.tres').read_text())
 manifest['characters'][cid]={'name':name,'row_pivots':pivots[cid],'moves':[m['sequence_id'] for m in authored],'status':vals['completion_status']}
(R/'moves/choreography.json').write_text(json.dumps(D,indent=2));(K/'battle_mapping.json').write_text(json.dumps(manifest,indent=2))
registry=json.loads((R/'moves/roster.json').read_text())
for cid in recipes:
 path=f'res://moves/{cid}.tres'
 if path not in registry:registry.append(path)
(R/'moves/roster.json').write_text(json.dumps(registry,indent=2))
print('10 packages / 40 prototype timelines')
