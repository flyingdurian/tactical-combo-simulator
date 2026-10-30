# Executed inside author_roster.py after the explicit recipes.
for cid,name,tint,idle in [('chunli','Chun-Li',[.35,.6,1],None),('xiaoyu','Ling Xiaoyu',[1,.63,.25],None),('reiji','Reiji Arisu',[.95,.4,.25],'d.9.3:60'),('xiaomu','Xiaomu',[1,.82,.3],'d.3.6:60'),('morrigan','Morrigan Aensland',[.72,.5,1],'i.0.0:60')]:
 ids={m['sequence_id'] for m in D['moves']}
 if cid+'_neutral' not in ids:continue
 slots=[f'res://moves/{cid}_{k}.tres' if cid+'_'+k in ids else '' for k in ['neutral','left','up','down','right']]
 special=[f'res://moves/{cid}_special_{i}.tres' if cid+'_special_'+str(i) in ids else '' for i in [1,2]]
 idlepose=pose(cid,idle) if idle else None
 vals={'character_id':cid,'display_name':name,'idle_texture':idlepose['path'] if idlepose else f'res://assets/characters/{cid}/frames/idle.png','native_facing':-1,'artwork_status':'Supplied assembled poses / provisional authored playback','main_sequences':slots,'assist_sequence':f'res://moves/{cid}_assist.tres','assist_variants':[f'res://moves/{cid}_assist.tres'],'special_sequences':special,'ultimate_sequence':f'res://moves/{cid}_ultimate.tres' if cid+'_ultimate' in ids else '', 'supported_roles':['main','assist'],'source_manifest':'res://assets/characters/roster_manifest.json','availability_note':'Prototype choreography. Empty slots unavailable. Native original timing unverified.','completion_status':'provisional'}
 vals['portrait_texture']=vals['idle_texture']
 lines=['[gd_resource type="Resource" script_class="CharacterDefinition" load_steps=2 format=3]','[ext_resource type="Script" path="res://battle/CharacterDefinition.gd" id="1"]','[resource]','script = ExtResource("1")']
 for k,v in vals.items():lines.append(k+' = '+('Array[String]('+json.dumps(v)+')' if isinstance(v,list) else json.dumps(v)))
 lines+=['pivot = Vector2('+','.join(map(str,idlepose['anchor'] if idlepose else [128,176]))+')','tint = Color('+','.join(map(str,tint))+',1)','effect_palette = Color('+','.join(map(str,tint))+',1)']
 if (R/f'sounds/{cid}.tres').exists():
  lines[0]=lines[0].replace('load_steps=2','load_steps=3')
  lines.insert(2,f'[ext_resource type="Resource" path="res://sounds/{cid}.tres" id="voice"]')
  lines.append('sound_profile = ExtResource("voice")')
 (R/f'moves/{cid}.tres').write_text('\n'.join(lines)+'\n')
MP.write_text(json.dumps(manifest,indent=2));(R/'moves/choreography.json').write_text(json.dumps(D,indent=2))
print('Saved',stage,len(D['moves']),'move recipes')
