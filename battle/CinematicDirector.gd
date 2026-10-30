class_name CinematicDirector
extends RefCounted
## Authored stage/summary ownership, separate from scheduler events and target motion.
var active: bool = false
var action_id: int = -1
var connected: bool = false
var reduced: bool = false
var shortened: bool = false
var shortened_rate: float = 1.8
var banner: String = ""
var cleanup_count: int = 0
var hits: int = 0
var damage: int = 0
var summary := Vector2i.ZERO
var summary_ticks: int = 0
var stage: String = ""
var miss_gate: int = 116
var release_tick: int = 366
var finishing: bool = false
var spec: Dictionary = {}
var title: String = "AETHER LANCE"
var character_name: String = "KOS-MOS"
var duration: int = 420
var beam_presentation: bool = true
func begin(id: int, move: SequenceData = null, character: CharacterDefinition = null) -> void:
	spec=move.cinematic_spec if move!=null else {}
	title=str(spec.get("title","AETHER LANCE"));character_name=character.display_name if character!=null else "KOS-MOS"
	duration=move.duration_ticks if move!=null else 420
	miss_gate=int(spec.get("miss_gate",116));release_tick=int(spec.get("release_tick",366))
	beam_presentation=str(spec.get("presentation","sustained_beam"))=="sustained_beam"
	active=true;action_id=id;connected=false;banner="KOS-MOS / AETHER LANCE";stage="CONFIRM"
	hits=0;damage=0;finishing=false;summary_ticks=0
func update(tick: int) -> void:
	if tick<30:stage="CONFIRM"
	elif tick<104:stage="DEPLOY / CHARGE"
	elif tick<360:stage="SUSTAINED DISCHARGE"
	elif tick<366:stage="FINAL DISCHARGE"
	else:stage="AFTERMATH"
	for marker in spec.get("stages",[]):
		if tick>=int(marker.tick):stage=str(marker.name)
	banner=character_name+" // "+title if stage=="CONFIRM" else title+" / "+stage
func finish() -> void:
	if active:
		cleanup_count+=1;summary=Vector2i(hits,damage);summary_ticks=180
	active=false;action_id=-1;connected=false;banner="";stage="";finishing=false
func reset() -> void:
	finish();cleanup_count=0;summary=Vector2i.ZERO;summary_ticks=0;hits=0;damage=0
