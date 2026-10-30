class_name TemporaryAudio
extends Node
## Original local synthesis, no actor imitation or downloaded audio. Eight reused voices.
var voices: Array[AudioStreamPlayer] = []
var cache: Dictionary = {}
var enabled: bool = true
var cinematic_duck: bool = false
var cursor: int = 0
func _ready() -> void:
	for i in range(8):
		var voice:=AudioStreamPlayer.new();add_child(voice);voices.append(voice)
	# Prepare short PCM layers once at scene startup, never allocate audio per hit.
	for layer in ["tap","crack","bass","energy","electric","activate","charge","finish","decay"]:cache[layer]=synthesize(layer)
func play(layer: String) -> void:
	if not enabled:return
	if not cache.has(layer):cache[layer]=synthesize(layer)
	var voice:=voices[cursor%voices.size()];cursor+=1
	voice.stop();voice.stream=cache[layer];voice.volume_db=-20 if cinematic_duck and layer in ["tap","crack"] else -14
	voice.play()
func synthesize(layer: String) -> AudioStreamWAV:
	var duration:=.14
	var pitch:=180.0
	match layer:
		"bass":duration=.35;pitch=60
		"charge":duration=1.15;pitch=130
		"activate":duration=.5;pitch=420
		"energy":duration=.24;pitch=650
		"electric":duration=.3;pitch=900
		"finish":duration=.65;pitch=48
		"decay":duration=.8;pitch=90
	var data:=PackedByteArray();data.resize(int(duration*22050)*2)
	var rng:=RandomNumberGenerator.new();rng.seed=layer.hash()
	for i in range(data.size()/2):
		var t:=i/22050.0;var progress:=t/duration
		var envelope:=pow(1-progress,2)*minf(1,t/.008)
		if layer=="charge":envelope=sin(progress*PI)*.65
		var wave:=sin(TAU*pitch*t*(1+progress*.3))*.65+rng.randf_range(-1,1)*.3
		data.encode_s16(i*2,int(clampf(wave*envelope,-1,1)*12000))
	var sound:=AudioStreamWAV.new();sound.format=AudioStreamWAV.FORMAT_16_BITS;sound.mix_rate=22050;sound.data=data
	return sound
func clear_all() -> void:
	for voice in voices:voice.stop();voice.stream=null
	cinematic_duck=false
