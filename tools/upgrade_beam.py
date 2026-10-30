from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'battle/CharacterDefinition.gd';p.write_text(p.read_text()+'\n@export var anchors: Dictionary = {}\n')
p=R/'battle/BattleActor.gd';s=p.read_text().replace('var pose_index: int = 0','var pose_anchors: Dictionary = {}\nvar pose_index: int = 0').replace('frame_anchor = definition.pivot','pose_anchors = definition.anchors.duplicate(true)\n\tframe_anchor = definition.pivot').replace('pose_index = i','pose_index = i\n\t\t\tpose_anchors.merge(pose.get("anchors", {}), true)');s+='''
# Source-pixel anchors use precisely the same transform as the displayed pose.
func anchor_world(key: String, fallback: Vector2 = Vector2.ZERO) -> Vector2:
	if not pose_anchors.has(key):return position+Vector2(fallback.x*facing,fallback.y-elevation)
	var xy: Array=pose_anchors[key]
	var local: Vector2=(Vector2(xy[0],xy[1])-frame_anchor)*definition.sprite_scale+pose_offset+authored_offset
	local.x*=facing*native_facing
	return position+local-Vector2(0,elevation)
''';p.write_text(s)
p=R/'moves/choreography.json';d=json.loads(p.read_text());m=next(x for x in d['moves'] if x['sequence_id']=='kosmos_ultimate');m['poses'][0]['anchors']={'grip_rear':[137,115],'grip_front':[118,109],'muzzle':[52,96]};m['purpose']='Continuous muzzle-anchored discharge; nine explicit exposure pulses; valid initial capture and final surge.'
for e in m['hit_events']:e['beam_width']=54 if e.get('ultimate_finish') else 34
p.write_text(json.dumps(d,indent=2))
p=R/'battle/CinematicDirector.gd';s=p.read_text().replace('elif tick<146:stage="INITIAL CONNECTION"\n\telif tick<304:stage="BARRAGE"\n\telif tick<360:stage="FINAL CHARGE"','elif tick<360:stage="SUSTAINED DISCHARGE"');p.write_text(s)
