from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'battle/SequenceData.gd';p.write_text(p.read_text()+'\n@export var cinematic_spec: Dictionary = {}\n')
p=R/'battle/CharacterDefinition.gd';p.write_text(p.read_text()+'''\n@export var portrait_region: Rect2 = Rect2(100,70,55,55)
@export var sound_profile: CharacterSoundProfile
@export var effect_palette: Color = Color.CYAN
@export var completion_status: String = "provisional"
@export var recovery_texture: String = ""
@export var defeat_texture: String = ""
''')
p=R/'battle/CinematicDirector.gd';s=p.read_text().replace('func begin(id: int) -> void:','''var spec: Dictionary = {}
var title: String = "AETHER LANCE"
var character_name: String = "KOS-MOS"
var duration: int = 420
var beam_presentation: bool = true
func begin(id: int, move: SequenceData = null, character: CharacterDefinition = null) -> void:''').replace('active=true;action_id=id;connected=false;','''spec=move.cinematic_spec if move!=null else {}
	title=str(spec.get("title","AETHER LANCE"));character_name=character.display_name if character!=null else "KOS-MOS"
	duration=move.duration_ticks if move!=null else 420
	miss_gate=int(spec.get("miss_gate",116));release_tick=int(spec.get("release_tick",366))
	beam_presentation=str(spec.get("presentation","sustained_beam"))=="sustained_beam"
	active=true;action_id=id;connected=false;''').replace('banner="KOS-MOS // AETHER LANCE" if stage=="CONFIRM" else "AETHER LANCE / "+stage','''for marker in spec.get("stages",[]):
		if tick>=int(marker.tick):stage=str(marker.name)
	banner=character_name+" // "+title if stage=="CONFIRM" else title+" / "+stage''');p.write_text(s)
p=R/'battle/TargetMotion.gd';s=p.read_text().replace('var captured_height: float = 0','var captured_height: float = 0\nvar capture_goal_height: float = 70').replace('lerpf(captured_height,70.0,','lerpf(captured_height,capture_goal_height,').replace('capture_age=0;recoil_left=0','capture_age=0;capture_goal_height=70;recoil_left=0');p.write_text(s)
p=R/'battle/BattleDemo.gd';s=p.read_text().replace('cinematic.begin(int(scheduler.actions[0].id))','cinematic.begin(int(scheduler.actions[0].id),move,actors[0].definition)').replace('weapon.active=true','weapon.active=cinematic.beam_presentation').replace('get("tick",420)','get("tick",cinematic.duration)').replace('weapon.active=action_tick<420','weapon.active=cinematic.beam_presentation and action_tick<cinematic.duration').replace('dummy.motion.begin_capture(cinematic.action_id,320)','dummy.motion.capture_goal_height=float(cinematic.spec.get("capture_height",70))\n\t\tdummy.motion.begin_capture(cinematic.action_id,mini(420,cinematic.release_tick-int(scheduler.actions.get(0,{}).get("tick",0))+30))').replace('"PROTOTYPE HEAVY-ENERGY DEPLOYMENT"','"PROTOTYPE CHOREOGRAPHY / "+str(cinematic.spec.get("motif","heavy energy"))').replace('Rect2(118,62,48,50)','actors[0].definition.portrait_region');p.write_text(s)
p=R/'moves/kosmos.tres';p.write_text(p.read_text()+'\nportrait_region = Rect2(118,62,48,50)\n')
p=R/'battle/MovePreview.gd';s=p.read_text().replace('cinematic.begin(int(scheduler.actions[0].id));','cinematic.begin(int(scheduler.actions[0].id),selected_move,definition);').replace('weapon.active=true','weapon.active=cinematic.beam_presentation');p.write_text(s)
