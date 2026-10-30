class_name CharacterVoice
extends Node
## Optional voice channel. No pitch variation, synthesis, or impact-sound substitution.
var profile:CharacterSoundProfile
var player:AudioStreamPlayer
var cooldown:=0.0
var priority:=-1
var enabled:=true
var cursors:Dictionary={}
var last_fallback:=""
func _ready()->void:
	player=AudioStreamPlayer.new();add_child(player)
func configure(value:CharacterSoundProfile)->void:
	reset();profile=value
func reset()->void:
	cooldown=0;priority=-1;cursors.clear();last_fallback=""
	if is_instance_valid(player):player.stop();player.stream=null
func advance(delta:float)->void:
	cooldown=maxf(0,cooldown-delta)
	if not enabled and is_instance_valid(player):player.stop()
func play_event(id:String)->bool:
	if not enabled:return false
	if profile==null:last_fallback="silence: no sound profile";return false
	var pool:Array=profile.clips.get(id,[])
	if pool.is_empty():last_fallback="silence: "+id;return false
	var requested:=int(profile.priorities.get(id,10))
	if cooldown>0 and requested<=priority:return false
	var index:=int(cursors.get(id,0))%pool.size()
	var path:=str(pool[index])
	if not ResourceLoader.exists(path):last_fallback="missing clip: "+path;return false
	var clip=load(path)
	if not clip is AudioStream:last_fallback="invalid clip: "+path;return false
	cursors[id]=index+1;priority=requested;cooldown=profile.cooldown_seconds
	player.stream=clip;player.volume_db=profile.volume_db;player.pitch_scale=1;player.play();return true
