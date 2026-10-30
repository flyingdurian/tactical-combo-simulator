class_name ImpactFX
extends Node2D
## Bounded, deterministic particle/damage list: reset clears everything immediately.
var electrical: ElectricalFX
var audio: TemporaryAudio
var profile_cache: Dictionary = {}
var reduced_flash: bool = false
var contact_effects: Array[Dictionary] = []
var last_number: Dictionary = {}
var numbers: Array[Dictionary] = []
var number_size: float = 1.0
var effect_density: float = 1.0
var wall_at := Vector2.ZERO
var wall_life: float = -1
var cross_at := Vector2.ZERO
var cross_life: float = -1
var cross_release: bool = false
var bursts: Array[Dictionary] = []
var trails: Array[Dictionary] = []
var flash_strength: float = 0.12
var shake_strength: float = 0.35
var shake_left: float = 0.0
var flash_left: float = 0.0
var audio_enabled: bool = true
var voices: Array[AudioStreamPlayer] = []
var sound: AudioStreamWAV
var voice_index: int = 0

func _ready() -> void:
	electrical=ElectricalFX.new();add_child(electrical)
	audio=TemporaryAudio.new();add_child(audio)

func profile_for(event: Dictionary) -> ImpactProfile:
	var path := str(event.get("impact_profile","res://impacts/light.tres"))
	if not profile_cache.has(path):profile_cache[path]=load(path) if ResourceLoader.exists(path) else load("res://impacts/light.tres")
	return profile_cache[path]

func present_contact(at: Vector2, damage: int, profile: ImpactProfile, target: BattleActor, direction: int) -> void:
	impact(at,damage,profile.profile_id,profile.camera_impulse)
	var burst: Dictionary=bursts[-1]
	burst.profile=profile;burst.direction=direction
	if not last_number.is_empty():
		last_number.profile=profile;last_number.heavy=profile.number_scale>=1.3
	flash_left=maxf(flash_left,profile.screen_flash) if not reduced_flash else 0
	electrical.discharge(target,profile,direction)
	target.rim_color=profile.color
	target.rim_left=4 if not reduced_flash else 0
	target.rim_strength=profile.rim_strength
	audio.enabled=audio_enabled
	for layer in profile.sound_layers:audio.play(layer)
	contact_effects.append({"at":at,"profile":profile.profile_id,"damage":damage})
	if contact_effects.size()>128:contact_effects.pop_front()

func impact(at: Vector2, damage: int, kind: String, strength: float) -> void:
	# Reuse a nearby rapid label while retaining the exact sum, maximum seven labels.
	var merged := false
	for label in numbers:
		if label.life < .12 and (label.at as Vector2).distance_to(at) < 65 and strength < 3:
			label.damage += damage; label.life = 0; last_number=label; merged = true; break
	if not merged:
		if numbers.size() >= 7: numbers.pop_front()
		numbers.append({"at":at,"life":0.0,"damage":damage,"heavy":strength>=3,"lane":numbers.size()%3})
		last_number=numbers[-1]
	bursts.append({"at": at, "life": 0.0, "damage": damage, "kind": kind, "index": bursts.size() % 4})
	if bursts.size() > 24:
		bursts.pop_front()
	shake_left = maxf(shake_left, strength * 0.025)

func play_impact_sound() -> void:
	audio.enabled=audio_enabled;audio.play("tap")

func wall_accent(at: Vector2) -> void:
	wall_at = at; wall_life = 0
	var p: ImpactProfile=load("res://impacts/wall.tres")
	bursts.append({"at":at,"life":0.0,"damage":0,"kind":"wall","index":0,"profile":p,"direction":-1 if at.x>640 else 1})
	audio.enabled=audio_enabled
	for layer in p.sound_layers:audio.play(layer)

func cross_accent(at: Vector2, releasing: bool = false) -> void:
	cross_at = at; cross_life = 0; cross_release = releasing
func advance(delta: float) -> void:
	electrical.density=effect_density
	electrical.advance(delta)
	for label in numbers: label.life += delta
	numbers = numbers.filter(func(n: Dictionary) -> bool: return n.life < .7)
	if cross_life >= 0: cross_life += delta
	if wall_life >= 0: wall_life += delta
	for trail in trails:
		trail.life += delta
	trails = trails.filter(func(t: Dictionary) -> bool: return t.life < 0.3)
	for burst in bursts:
		burst.life += delta
	bursts = bursts.filter(func(b: Dictionary) -> bool: return b.life < 0.85)
	shake_left = maxf(0, shake_left - delta)
	flash_left = maxf(0, flash_left - delta)
	queue_redraw()

func clear_all() -> void:
	electrical.clear_all()
	audio.clear_all()
	contact_effects.clear()
	numbers.clear()
	last_number={}
	cross_life = -1
	wall_life = -1
	bursts.clear()
	trails.clear()
	shake_left = 0
	flash_left = 0
	for voice in voices:
		voice.stop()
	queue_redraw()

func _draw() -> void:
	if wall_life >= 0 and wall_life < .65:
		var at := Vector2(clampf(wall_at.x-85,24,1080),wall_at.y-42)
		draw_string_outline(ThemeDB.fallback_font,at,"WALL BOUNCE",HORIZONTAL_ALIGNMENT_LEFT,-1,20,4,Color("172637"))
		draw_string(ThemeDB.fallback_font,at,"WALL BOUNCE",HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("8fe3ff"))
		draw_arc(wall_at,22+wall_life*65,0,TAU,24,Color(.5,.9,1,1-wall_life/.65),3)
	for trail in trails:
		draw_line(trail.from + Vector2(0,-65), trail.to + Vector2(0,-65), Color(0.5,0.9,1,0.3-trail.life), 12)
	for burst in bursts:
		var p: ImpactProfile=burst.get("profile",profile_for({}))
		var t: float=burst.life
		var at: Vector2=burst.at
		var fade:=maxf(0,1-t/maxf(.12,p.lingering))
		if fade<=0:continue
		var direction:=int(burst.get("direction",1))
		var radius:=p.radius*(.45+minf(1,t*12))
		# Primary silhouette remains visible at density zero; secondary detail scales down.
		var star:=PackedVector2Array()
		for i in range(8):
			var angle:=i*TAU/8
			var length:=radius if i%2==0 else radius*.18
			star.append(at+Vector2(cos(angle)*length,sin(angle)*length*.6))
		draw_colored_polygon(star,Color(p.color,fade*.8))
		draw_line(at-Vector2(radius*.7,0),at+Vector2(radius*.9,0),Color(p.core_color,fade),3)
		if p.shock_ring:draw_arc(at,radius*(.7+t*2),0,TAU,32,Color(p.color,fade*.65),2)
		for i in range(clampi(roundi(p.spark_count*effect_density),0,18)):
			var angle:=i*2.399+float(burst.index)
			var ray:=Vector2(cos(angle),sin(angle))
			draw_line(at+ray*(10+t*80),at+ray*(18+t*190),Color(p.color,fade),2)
		for i in range(clampi(roundi(p.directional_streaks*effect_density),0,8)):
			var y: float=(i-p.directional_streaks*.5)*8
			var start:=at+Vector2(direction*(8+t*60),y)
			draw_line(start,start+Vector2(direction*(22+t*140),y*.2),Color(p.color,fade*.8),3)
		for i in range(clampi(roundi(p.debris*effect_density),0,8)):
			var drift:=Vector2(direction*(20+i*7)*t*4,-(60+i*17)*t+280*t*t)
			draw_rect(Rect2(at+drift,Vector2(3+i%3,3)),Color(p.color.darkened(.4),fade))
	for label in numbers:
		var t: float = label.life
		var at: Vector2 = label.at + Vector2(12+label.lane*14,-18-t*48)
		var alpha := minf(1,(.7-t)*4)
		var p: ImpactProfile=label.get("profile",profile_for({}))
		var size := roundi(28*p.number_scale*number_size*(1+.24*maxf(0,1-t/.12)))
		var color := Color(1,.68,.30,alpha) if label.heavy else Color(.93,.98,1,alpha)
		draw_string_outline(ThemeDB.fallback_font,at,str(label.damage),HORIZONTAL_ALIGNMENT_LEFT,-1,size,5,Color(.035,.06,.1,alpha))
		draw_string(ThemeDB.fallback_font,at,str(label.damage),HORIZONTAL_ALIGNMENT_LEFT,-1,size,color)
	if cross_life >= 0 and cross_life < .35:
		var alpha := 1-cross_life/.35
		var radius := (54+cross_life*150) if cross_release else (98-cross_life*110)
		for side in [-1,1]:
			var diagonal := Vector2(radius,side*radius*.65)
			draw_line(cross_at-diagonal,cross_at+diagonal,Color(.45,.85,1,alpha*.6),12)
			draw_line(cross_at-diagonal,cross_at+diagonal,Color(1,.91,.54,alpha),3)

func _exit_tree() -> void:
	# Stop voices before scene removal/reset to release active playback ownership.
	for voice in voices:
		if is_instance_valid(voice):
			voice.stop()
			voice.stream = null
	voices.clear()
	sound = null
