from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'moves/choreography.json';d=json.loads(p.read_text());m=next(x for x in d['moves'] if x['sequence_id']=='kosmos_ultimate')
for pose in m['poses']:pose['anchors']['muzzle']=[135,101];pose['mapping_status']='Inspected upper-torso chest emitter anchor; animated aperture overlay is prototype.'
for e in m['hit_events']:e['beam_width']=78 if e.get('ultimate_finish') else 54
p.write_text(json.dumps(d,indent=2))
p=R/'battle/HeavyEnergyRig.gd';s=p.read_text().replace('54.0 if tick>=350 else 34.0','78.0 if tick>=350 else 54.0').replace('var width:float=beam.width','var width:float=beam.width*(1.0+.065*sin(tick*.44))').replace('width*.32','width*.43').replace('width*.13','width*.2')
s=s.replace('var muzzle:=source()', '''var muzzle:=source()
		var opening:=smoothstep(30,95,tick)*(1-smoothstep(366,408,tick))
		for petal in range(6):
			var a:=petal*TAU/6+sin(tick*.02)*.12
			var radial:=Vector2(cos(a),sin(a));var tangent:=Vector2(-radial.y,radial.x)
			var at:=muzzle+radial*(5+opening*8)
			draw_colored_polygon(PackedVector2Array([at+radial*6,at+tangent*4,at-radial*3,at-tangent*4]),Color(.65,.88,1,opening*.8))''');p.write_text(s)
p=R/'battle/BattleDemo.gd';s=p.read_text();a=s.index('\t\tcpu_queue.assign(');b=s.index('\n\t\tcpu_assists_left.assign',a)
s=s[:a]+'''\t\tvar available:Array[String]=[]
		for path in data.main_sequences:
			if not path.is_empty() and ResourceLoader.exists(path):available.append(path)
		cpu_queue.clear()
		if not available.is_empty():
			for i in range(3):cpu_queue.append(available[cpu_rng.randi_range(0,available.size()-1)])
		var specials:Array[String]=[]
		for path in data.special_sequences:
			if not path.is_empty() and ResourceLoader.exists(path) and cpu_meter>=(load(path) as SequenceData).resource_cost:specials.append(path)
		if not specials.is_empty() and cpu_queue.size()>1:
			cpu_queue[1]=specials[cpu_rng.randi_range(0,specials.size()-1)]
			cpu_meter-=(load(cpu_queue[1]) as SequenceData).resource_cost
''' +s[b:];p.write_text(s)
p=R/'battle/PackageValidator.gd';s=p.read_text().replace('normal_paths[path]=true','if not path.is_empty():normal_paths[path]=true');p.write_text(s)
