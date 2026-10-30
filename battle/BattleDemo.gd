class_name BattleDemo
extends Node2D
## Alternating match owner. Attack timelines, staging, motion and defense are separate systems.
enum Phase { MatchIntro, PlayerAttackPhase, PhaseResolution, CPUAttackPhase, Victory, Defeat, Reset, Ultimate }
var presentation := PresentationController.new()
var backdrop: CinematicBackdrop
var weapon: HeavyEnergyRig
var cinematic := CinematicDirector.new()
var ultimate_used: bool = false
var rules: DemoRules = load("res://moves/demo_rules.tres")
var defense := DefenseController.new()
var player_hp: int = 120
var versus_mode:bool=true
var cpu_team:Array[int]=[3,4,5]
var cpu_actors:Array[BattleActor]=[]
var cpu_queue:Array[String]=[]
var cpu_wait:int=0
var cpu_assists_left:Array[int]=[]
var cpu_meter:int=0
var cpu_rng:=RandomNumberGenerator.new()
var cpu_round: int = 0
var cpu_log: Array[Dictionary] = []
var defense_text: String = ""
var defense_text_ticks: int = 0
var projectiles: ProjectileSystem
var scheduler := AttackScheduler.new()
var meter := CombatMeter.new()
var definitions: Array[CharacterDefinition] = CharacterCatalog.load_all()
var roles: Array[int] = [0, 1, 2]
var actors: Array[BattleActor] = []
var dummy: BattleActor
var world: Node2D
var fx: ImpactFX
var phase: Phase = Phase.MatchIntro
var phase_ticks: int = 0
var resolution_from: Phase = Phase.PlayerAttackPhase
var charges: int = 3
var assist_used: Array[bool] = [false, false]
var special_used: bool = false
var special_slots_used: Array[bool] = [false,false]
var cancel_bonus_used: int = 0
var cancel_slow_left: int = 0
var cancel_followup_left: int = 0
var cancel_log: Array[Dictionary] = []
var grace_left: int = 150
var buffer_slot: int = -1
var buffer_left: int = 0
var hp: int = 400
var combo: int = 0
var total_damage: int = 0
var combo_damage: int = 0
var final_combo: Vector2i = Vector2i.ZERO
var final_combo_ticks: int = 0
var increment_ticks: int = 0
var milestone_hits: int = 0
var milestone_ticks: int = 0
var previous_cross: int = 0
var wall_event_count: int = 0
var hitstop: int = 0
var sim_tick: int = 0
var cross_count: int = 0
var cross_cooldown: int = 0
var cross_text: int = 0
var last_main: int = -10000
var last_assist: int = -10000
var consumed: Dictionary = {}
var hit_log: Array[Dictionary] = []
var feedback: String = "J: KOS-MOS sequence | U / I: independent assists"
var feedback_good: bool = true
var feedback_ticks: int = 0
var infinite_hp: bool = false
var infinite_player_hp: bool = false
var infinite_meter: bool = false
var ai_on: bool = true
var logging: bool = false
var slow: bool = false
var accumulator: float = 0
var debug_panel: PanelContainer
var role_pickers: Array[OptionButton] = []
var variant_pickers:Array[OptionButton]=[]
var pending_roles:Array[int]=[0,1,2]
var assist_variants:Array[int]=[0,0]
var pending_variants:Array[int]=[0,0]
var roster_status:Label
var preview_only: bool = false
var mode: String = "NORMAL"
var contact_log: Array[Dictionary] = []
var effects_enabled: bool = true
var hud: Node2D

func _ready() -> void:
	world = Node2D.new()
	add_child(world)
	world.add_child(UrbanArena.new())
	for i in range(3):
		var actor := BattleActor.new()
		world.add_child(actor)
		actors.append(actor)
		actor.z_index = 3 + i
	dummy = BattleActor.new()
	dummy.target_dummy = true
	world.add_child(dummy)
	var def := CharacterDefinition.new()
	def.display_name = "Training CPU"
	def.tint = Color("fa806d")
	dummy.configure(def, Vector2(890, 520))
	cpu_rng.randomize()
	cpu_actors.append(dummy)
	for i in range(2):
		var partner:=BattleActor.new();world.add_child(partner);partner.z_index=4+i;cpu_actors.append(partner)
	projectiles = ProjectileSystem.new()
	world.add_child(projectiles)
	projectiles.z_index = 10
	projectiles.connected.connect(_on_projectile_contact)
	projectiles.missed.connect(_on_projectile_miss)
	fx = ImpactFX.new()
	world.add_child(fx)
	fx.z_index = 20
	weapon=HeavyEnergyRig.new();weapon.attacker=actors[0];weapon.target=dummy;weapon.z_index=8
	world.add_child(weapon)
	backdrop=CinematicBackdrop.new();backdrop.director=cinematic;backdrop.fighter=actors[0];backdrop.z_index=1;world.add_child(backdrop)
	scheduler.hit_event.connect(_on_hit)
	scheduler.cue_event.connect(_on_cue)
	hud = Node2D.new()
	hud.z_index = 50
	hud.draw.connect(draw_hud.bind(hud))
	add_child(hud)
	for entry in [[Vector2(30, 10), "CROSS / CIRCUIT", 25], [Vector2(340, 13), "IMPACT / F3 SIDE / F4 MISS", 18], [Vector2(1035, 15), "R RESET / F1 DEBUG", 15]]:
		var label := Label.new()
		label.position = entry[0]
		label.text = entry[1]
		label.add_theme_font_size_override("font_size", entry[2])
		label.z_index = 51
		add_child(label)
	_build_debug()
	reset_match()

func reset_match() -> void:
	phase = Phase.Reset
	cinematic.reset()
	if weapon:weapon.clear_all()
	if world:presentation.reset(world)
	ultimate_used = false
	mode = "NORMAL"
	defense.reset()
	defense.perfect_window = rules.perfect_block_ticks
	defense.dodge_window = rules.dodge_ticks
	defense.dodge_recovery = rules.dodge_recovery_ticks
	defense.dodge_cooldown = rules.dodge_cooldown_ticks
	defense.block_factor = rules.block_damage_factor
	defense.perfect_factor = rules.perfect_damage_factor
	player_hp = rules.target_hp if versus_mode else rules.player_hp
	cpu_round = 0
	cpu_log.clear()
	cpu_queue.clear();cpu_assists_left.clear();cpu_wait=0;cpu_meter=0
	if versus_mode:
		var pool:Array[int]=[]
		for i in range(definitions.size()):pool.append(i)
		for i in range(3):
			var selected:=cpu_rng.randi_range(0,pool.size()-1)
			cpu_team[i]=pool.pop_at(selected)
		for i in range(3):
			cpu_actors[i].target_dummy=false
			cpu_actors[i].configure(definitions[cpu_team[i]],Vector2(890+i*65,520))
			cpu_actors[i].motion.reset();cpu_actors[i].visible=i==0
	else:
		dummy.target_dummy=true
		var placeholder:=CharacterDefinition.new();placeholder.display_name="Training CPU";placeholder.tint=Color("fa806d")
		dummy.configure(placeholder,Vector2(890,520))
		for i in range(1,3):cpu_actors[i].visible=false
	defense_text = ""
	defense_text_ticks = 0
	contact_log.clear()
	scheduler.reset()
	projectiles.reset()
	fx.clear_all()
	consumed.clear()
	hit_log.clear()
	buffer_slot = -1
	buffer_left = 0
	hitstop = 0
	combo = 0
	total_damage = 0
	combo_damage = 0
	final_combo = Vector2i.ZERO
	final_combo_ticks = 0
	increment_ticks = 0
	milestone_hits = 0
	milestone_ticks = 0
	previous_cross = 0
	wall_event_count = 0
	sim_tick = 0
	last_main = -10000
	last_assist = -10000
	cross_count = 0
	cross_cooldown = 0
	cross_text = 0
	accumulator = 0
	meter.maximum = rules.meter_maximum
	meter.value = meter.maximum if infinite_meter else 0
	cancel_bonus_used = 0
	cancel_slow_left = 0
	cancel_followup_left = 0
	cancel_log.clear()
	special_slots_used = [false,false]
	presentation.reset(world)
	hp = rules.target_hp
	dummy.home = Vector2(890, 520)
	dummy.motion.reset()
	dummy.sample({})
	dummy.motion.juggle_limit = rules.juggle_limit
	for i in range(3):
		actors[i].configure(definitions[roles[i]], Vector2(315 - i * 70, 520))
		actors[i].motion.reset()
		actors[i].release_ticks = 0
		actors[i].cosmetic_dodge = false
		actors[i].visible = i == 0
		actors[i].sample({})
	charges = rules.sequence_charges
	assist_used = [false, false]
	special_used = false
	phase = Phase.MatchIntro
	phase_ticks = 0
	grace_left = rules.grace_ticks
	notify_action("RESET / new training run", true)

func notify_action(message: String, accepted: bool) -> void:
	feedback = message
	feedback_good = accepted
	feedback_ticks = 90

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.echo: return
	if event.is_action("cancel_block"):
		if phase == Phase.CPUAttackPhase: defense.block(event.is_pressed())
		elif event.is_pressed(): request_cancel()
		return
	if not event.is_pressed(): return
	if event.is_action_pressed("reset_match"): reset_match()
	elif event.is_action_pressed("debug_panel"): debug_panel.visible = not debug_panel.visible
	elif event.is_action_pressed("move_lab"): get_tree().change_scene_to_file("res://scenes/MovePreview.tscn")
	elif event.is_action_pressed("swap_sides"): mirror_setup()
	elif event.is_action_pressed("miss_test"): miss_setup()
	elif event.is_action_pressed("late_test"): late_setup()
	elif event.is_action_pressed("toggle_cpu"):
		ai_on = not ai_on
		notify_action("CPU enabled" if ai_on else "TRAINING / CPU disabled",true)
	elif event.is_action_pressed("attack"): request_main(BattleCommands.capture())
	elif event.is_action_pressed("assist_1"): request_assist(1)
	elif event.is_action_pressed("assist_2"): request_assist(2)
	elif event.is_action_pressed("special_1"): request_main(5)
	elif event.is_action_pressed("special_2"): request_main(6)
	elif event.is_action_pressed("ultimate"): request_main(7)
	elif event.is_action_pressed("dodge"):
		var accepted := phase == Phase.CPUAttackPhase and defense.dodge()
		notify_action("DODGE" if accepted else "REJECTED / dodge requires CPU phase and ready cooldown",accepted)

func move_path(slot: int) -> String:
	var data := definitions[roles[0]]
	if slot < 0 or slot > 7: return ""
	if slot < 5: return data.main_sequences[slot] if slot < data.main_sequences.size() else ""
	if slot < 7: return data.special_sequences[slot-5] if slot-5 < data.special_sequences.size() else ""
	return data.ultimate_sequence

func move_name(slot: int) -> String:
	var path := move_path(slot)
	return (load(path) as SequenceData).display_name if not path.is_empty() and ResourceLoader.exists(path) else "UNAUTHORED"

func move_cost(slot: int) -> int:
	var path := move_path(slot)
	return (load(path) as SequenceData).resource_cost if not path.is_empty() and ResourceLoader.exists(path) else 0

func request_main(slot: int) -> bool:
	if hp <= 0 or phase != Phase.PlayerAttackPhase:
		notify_action("REJECTED / requires player phase and valid target",false); return false
	var path := move_path(slot)
	if path.is_empty() or not ResourceLoader.exists(path):
		notify_action("NOT AUTHORED / selected role or move",false); return false
	var selected: SequenceData = load(path)
	if slot < 5 and charges <= 0:
		notify_action("REJECTED / no normal actions left",false); return false
	if slot == 7:
		if ultimate_used or not scheduler.actions.is_empty() or not projectiles.shots.is_empty():
			notify_action("REJECTED / ultimate needs a clear stage (finish main / assists / arrows)",false); return false
	if meter.value < selected.resource_cost:
		notify_action("REJECTED / needs %d meter" % selected.resource_cost,false); return false
	if slot in [5,6] and special_slots_used[slot-5]:
		notify_action("REJECTED / that special used this phase",false); return false
	if scheduler.busy(0):
		var action: Dictionary = scheduler.actions[0]
		var current: SequenceData = action.move
		if int(action.tick) < current.chain_open - rules.buffer_ticks or int(action.tick) > current.chain_close:
			notify_action("REJECTED / outside chain buffer window",false); return false
		if buffer_slot >= 0:
			notify_action("REJECTED / queue already holds " + move_name(buffer_slot),false); return false
		buffer_slot = slot
		buffer_left = rules.buffer_ticks
		notify_action("BUFFERED / " + selected.display_name,true)
		_try_buffer()
		return true
	return _start_main(slot)

func _start_main(slot: int) -> bool:
	if hp <= 0:
		notify_action("COMMAND REJECTED / target defeated before execution",false); return false
	var path := move_path(slot)
	if path.is_empty() or not ResourceLoader.exists(path): return false
	var move: SequenceData = load(path)
	if (slot < 5 and charges <= 0) or meter.value < move.resource_cost:
		notify_action("REJECTED / resources changed before execution",false); return false
	if scheduler.start(0,move):
		meter.spend(move.resource_cost)
		AttackStaging.prepare(scheduler.actions[0],actors[0],dummy,mode == "MISS TEST")
		if slot < 5: charges -= 1
		elif slot < 7: special_slots_used[slot-5] = true
		if slot == 7:
			ultimate_used = true
			cinematic.begin(int(scheduler.actions[0].id),move,actors[0].definition)
			presentation.claim("ultimate",100)
			weapon.clear_all()
			weapon.active=cinematic.beam_presentation
			fx.audio.cinematic_duck=true
			phase = Phase.Ultimate
		grace_left = rules.grace_ticks
		cancel_followup_left = 0
		notify_action("ACCEPTED / " + move.display_name,true)
		return true
	return false

func _try_buffer() -> void:
	if buffer_slot < 0: return
	if scheduler.busy(0):
		var action: Dictionary = scheduler.actions[0]
		var move: SequenceData = action.move
		if int(action.tick) < move.chain_open: return
		if int(action.tick) > move.chain_close:
			buffer_slot = -1
			notify_action("BUFFER EXPIRED / chain window closed",false); return
		# Authored normal chain point ends the previous timeline; target motion is untouched.
		_end_main(false)
	var slot := buffer_slot
	buffer_slot = -1
	_start_main(slot)

func _end_main(recover: bool) -> Dictionary:
	var ended := scheduler.cancel(0)
	if ended.is_empty(): return ended
	if ended.move.cancel_projectiles: projectiles.cancel_owned(int(ended.id))
	fx.trails = fx.trails.filter(func(t: Dictionary) -> bool: return int(t.get("owner",-1)) != int(ended.id))
	if recover: actors[0].release_action()
	return ended

func request_cancel() -> bool:
	if phase != Phase.PlayerAttackPhase or not scheduler.busy(0):
		notify_action("REJECTED / no player sequence to cancel",false); return false
	var action: Dictionary = scheduler.actions[0]
	var move: SequenceData = action.move
	if int(action.tick) < move.cancel_open or int(action.tick) > move.cancel_close:
		notify_action("REJECTED / outside authored CANCEL window",false); return false
	if not meter.spend(rules.cancel_cost):
		notify_action("REJECTED / cancel needs %d meter" % rules.cancel_cost,false); return false
	var ended := _end_main(true)
	if cancel_bonus_used < rules.cancel_extra_actions_per_phase:
		charges += 1; cancel_bonus_used += 1
	cancel_slow_left = rules.cancel_slow_ticks
	cancel_followup_left = rules.cancel_followup_ticks
	grace_left = rules.cancel_followup_ticks
	fx.flash_left = .12
	cancel_log.append({"id":ended.id,"tick":ended.tick,"sim_tick":sim_tick,"cost":rules.cancel_cost})
	notify_action("CANCEL / future strikes removed; follow up now",true)
	# A previously accepted command is transferred, never silently discarded.
	_try_buffer()
	return true

func request_assist(actor: int) -> bool:
	if hp <= 0:
		notify_action("REJECTED / no valid target",false)
		return false
	if phase != Phase.PlayerAttackPhase or actor < 1 or actor > 2:
		notify_action("REJECTED / assists require Player Attack Phase", false)
		return false
	if assist_used[actor - 1]:
		notify_action("REJECTED / assist already used this phase", false)
		return false
	var definition:=definitions[roles[actor]]
	var choices:=definition.assist_variants
	var path:String=choices[assist_variants[actor-1]] if assist_variants[actor-1]<choices.size() else definition.assist_sequence
	if path.is_empty() or not ResourceLoader.exists(path):
		notify_action("NOT AUTHORED / assigned assist", false)
		return false
	var move: SequenceData = load(path)
	if scheduler.start(actor, move):
		# The first assist uses the far side while the main is committed nearby.
		if actor == 1 and scheduler.busy(0):
			scheduler.actions[actor].entry_facing = -actors[0].facing
		AttackStaging.prepare(scheduler.actions[actor], actors[actor], dummy, mode == "MISS TEST")
		assist_used[actor - 1] = true
		grace_left = rules.grace_ticks
		notify_action("ASSIST / " + definitions[roles[actor]].display_name, true)
		return true
	return false

func request_special() -> bool:
	return request_main(5)

func _physics_process(_delta: float) -> void:
	if preview_only:
		return
	var rate := 0.25 if slow else 1.0
	if cinematic.active and cinematic.shortened:rate *= cinematic.shortened_rate
	if cancel_slow_left > 0:
		cancel_slow_left -= 1
		rate *= rules.cancel_slow_rate
	accumulator += rate
	while accumulator >= 1.0:
		accumulator -= 1.0
		simulate_tick()

func simulate_tick() -> void:
	sim_tick += 1
	cinematic.summary_ticks=maxi(0,cinematic.summary_ticks-1)
	feedback_ticks = maxi(0, feedback_ticks - 1)
	cross_text = maxi(0, cross_text - 1)
	cross_cooldown = maxi(0, cross_cooldown - 1)
	if infinite_meter:
		meter.value = meter.maximum
	if hitstop > 0:
		hitstop -= 1
		return
	defense.advance()
	cancel_followup_left = maxi(0,cancel_followup_left-1)
	for actor in actors + cpu_actors: actor.advance_release()
	actors[0].cosmetic_dodge = defense.tick < defense.dodge_until
	defense_text_ticks = maxi(0,defense_text_ticks-1)
	actors[0].motion.advance()
	dummy.motion.origin_x = dummy.home.x
	actors[0].motion.origin_x = actors[0].home.x
	dummy.motion.advance()
	final_combo_ticks = maxi(0,final_combo_ticks-1)
	increment_ticks = maxi(0,increment_ticks-1)
	milestone_ticks = maxi(0,milestone_ticks-1)
	if dummy.motion.settled() and combo > 0:
		final_combo = Vector2i(combo,combo_damage)
		final_combo_ticks = 180
		combo = 0
		combo_damage = 0
	if previous_cross > 0 and dummy.motion.cross_ticks == 0 and effects_enabled:
		fx.cross_accent(dummy.position+Vector2(0,-90-dummy.elevation),true)
	previous_cross = dummy.motion.cross_ticks
	if dummy.motion.wall_events.size()>wall_event_count:
		wall_event_count = dummy.motion.wall_events.size()
		var bounce: Dictionary=dummy.motion.wall_events[-1]
		if effects_enabled: fx.wall_accent(Vector2(float(bounce.x),430-float(bounce.height)))
		var wall_profile:=fx.profile_for({"impact_profile":"res://impacts/wall.tres"})
		presentation.accent(-1 if float(bounce.x)>640 else 1,wall_profile.camera_impulse)
		hitstop=maxi(hitstop,wall_profile.hitstop)
		notify_action("WALL BOUNCE / boundary contact — continue now",true)
	for actor in actors:
		actor.opponent_x = dummy.home.x + dummy.motion.displacement
	dummy.sample({})
	for key in scheduler.actions:
		AttackStaging.advance_segments(scheduler.actions[key],cpu_actors[key-3] if key >= 3 else actors[key],actors[0] if key >= 3 else dummy)
		AttackStaging.align(scheduler.actions[key], actors[0] if key >= 3 else dummy)
	scheduler.advance()
	if cinematic.active:
		var action_tick:=int(scheduler.actions.get(0,{}).get("tick",cinematic.duration))
		cinematic.update(action_tick)
		weapon.tick=action_tick
		weapon.active=cinematic.beam_presentation and action_tick<cinematic.duration
		presentation.reduced=cinematic.reduced
		var middle: Vector2=(actors[0].position+dummy.position)*.5+Vector2(0,-100)
		var focus:=actors[0].position+Vector2(60,-90) if action_tick<104 else middle
		var zoom:=1.1 if action_tick<104 else 1.04 if action_tick<146 else 1.08 if action_tick<304 else 1.02 if action_tick<366 else 1.0
		presentation.frame("ultimate",focus,zoom)
		if action_tick>=cinematic.release_tick:dummy.motion.end_capture(cinematic.action_id,cinematic.finishing or hp<=0)
	projectiles.advance(dummy.hurt_region(),actors[0].hurt_region())
	_try_buffer()
	if buffer_slot >= 0:
		buffer_left -= 1
		if buffer_left <= 0:
			buffer_slot = -1
			notify_action("BUFFER EXPIRED / press closer to CHAIN", false)
	for i in range(3):
		actors[i].visible = i == 0 or scheduler.busy(i)
		actors[i].sample(scheduler.actions.get(i, {}))
	dummy.opponent_x = actors[0].position.x
	for i in range(3):
		cpu_actors[i].opponent_x=actors[0].position.x
		cpu_actors[i].visible=i==0 or scheduler.busy(i+3)
		cpu_actors[i].sample(scheduler.actions.get(i+3,{}))
	phase_ticks += 1
	match phase:
		Phase.Ultimate:
			if scheduler.busy(0) and int(scheduler.actions[0].tick)>cinematic.miss_gate and not cinematic.connected:
				_end_main(true)
				_finish_cinematic("ULTIMATE WHIFF / no valid entry contact")
			elif not scheduler.busy(0) and projectiles.shots.is_empty():
				_finish_cinematic("ULTIMATE RESOLVED / continue or end phase")
		Phase.MatchIntro:
			if phase_ticks >= rules.intro_ticks:
				_begin_player_phase()
		Phase.PlayerAttackPhase:
			if (scheduler.actions.is_empty() and projectiles.shots.is_empty()):
				grace_left -= 1
				if hp <= 0 or grace_left <= 0 or (charges == 0 and assist_used[0] and assist_used[1] and not meter_action_available()):
					resolution_from = Phase.PlayerAttackPhase
					phase = Phase.PhaseResolution
					phase_ticks = 0
		Phase.PhaseResolution:
			if (scheduler.actions.is_empty() and projectiles.shots.is_empty()) and dummy.motion.settled() and phase_ticks >= 30:
				if hp <= 0:
					phase = Phase.Victory
				elif player_hp <= 0:
					phase = Phase.Defeat
				elif resolution_from == Phase.PlayerAttackPhase:
					_begin_cpu_phase()
				else:
					_begin_player_phase()
		Phase.CPUAttackPhase:
			if versus_mode:_advance_roster_cpu()
			if cpu_queue.is_empty() and cpu_wait==0 and scheduler.actions.is_empty() and projectiles.shots.is_empty() and actors[0].motion.settled():
				resolution_from = Phase.CPUAttackPhase
				phase = Phase.PhaseResolution
				phase_ticks = 0

func _finish_cinematic(message: String) -> void:
	dummy.motion.end_capture(cinematic.action_id,cinematic.finishing or hp<=0)
	cinematic.finish()
	weapon.stop()
	fx.audio.cinematic_duck=false
	presentation.release("ultimate")
	cancel_slow_left = 0
	for i in range(3): actors[i].visible = i == 0 or scheduler.busy(i)
	phase = Phase.PlayerAttackPhase
	phase_ticks = 0
	grace_left = rules.grace_ticks
	notify_action(message,true)

func meter_action_available() -> bool:
	for slot in range(5,8):
		if slot<7 and special_slots_used[slot-5]: continue
		if slot==7 and ultimate_used: continue
		var path := move_path(slot)
		if not path.is_empty() and ResourceLoader.exists(path) and meter.value >= (load(path) as SequenceData).resource_cost: return true
	return false

func _begin_player_phase() -> void:
	phase = Phase.PlayerAttackPhase
	phase_ticks = 0
	charges = rules.sequence_charges
	assist_used = [false, false]
	special_used = false
	special_slots_used = [false,false]
	ultimate_used = false
	cancel_bonus_used = 0
	grace_left = rules.grace_ticks
	cross_count = 0
	last_main = -10000
	last_assist = -10000
	combo = 0
	notify_action("YOUR TURN / direction + J sequence / U I assists / Space cancel", true)

func _on_hit(actor: int, move: SequenceData, event: Dictionary, token: String) -> void:
	if actor >= 3:
		_resolve_cpu_hit(move,event,token,actor)
		return
	if consumed.has(token):
		return
	if hp <= 0 and move.category!="ultimate":
		return
	# Sample this tick BEFORE collision, rather than using last frame's transform.
	AttackStaging.align(scheduler.actions.get(actor, {}), dummy)
	actors[actor].opponent_x = dummy.home.x
	actors[actor].sample(scheduler.actions.get(actor, {}))
	dummy.sample({})
	var context := {"position":actors[actor].position,"elevation":actors[actor].elevation,"facing":actors[actor].facing,
		"commit_tick":scheduler.actions.get(actor,{}).get("stage",{}).get("commit_tick",-1),
		"aim":scheduler.actions.get(actor,{}).get("stage",{}).get("aim",dummy.position+Vector2(0,-90-dummy.elevation))}
	if event.get("kind", "melee") == "beam":
		weapon.tick=int(scheduler.actions.get(actor,{}).get("tick",0))
		var region:=weapon.emit_beam(event,token,dummy.motion.owner==TargetMotion.Owner.Cinematic)
		context.beam_source=weapon.source()
		_resolve_player_contact(actor,move,event,token,region,context)
		return
	if event.get("kind", "melee") == "projectile":
		projectiles.fire(actor,move,event,token,actors[actor],context)
		return
	_resolve_player_contact(actor,move,event,token,actors[actor].strike_region(event),context)

func _resolve_player_contact(actor: int, move: SequenceData, event: Dictionary, token: String, strike: Rect2, context: Dictionary) -> void:
	if consumed.has(token): return
	var hurt := dummy.hurt_region()
	var reason := contact_reason(strike, hurt)
	if reason == "CONTACT":
		if event.get("eligible","any")=="airborne" and dummy.motion.height<=0: reason="target grounded / airborne-only strike"
		if event.get("eligible","any")=="grounded" and dummy.motion.height>0: reason="target airborne / grounded-only strike"
	var record_attempt := {"token": token, "actor": actor, "sequence": move.sequence_id, "tick": sim_tick,
		"attacker": context.position, "attacker_elevation": context.elevation,
		"target": dummy.position, "target_elevation": dummy.elevation, "strike": strike, "hurt": hurt,
		"commit_tick": context.commit_tick, "result": reason}
	contact_log.append(record_attempt)
	if logging: print("CONTACT ", record_attempt)
	if reason != "CONTACT":
		if scheduler.actions.has(actor) and int(scheduler.actions[actor].tick) == int(event.get("end_tick", event.tick)):
			notify_action("MISS / " + reason, false)
		return
	consumed[token] = true
	if cinematic.active and actor==0 and move.category=="ultimate" and event.get("capture",false):
		cinematic.connected=true
		dummy.motion.capture_goal_height=float(cinematic.spec.get("capture_height",70))
		dummy.motion.begin_capture(cinematic.action_id,mini(420,cinematic.release_tick-int(scheduler.actions.get(0,{}).get("tick",0))+30))
	var contact := strike.intersection(hurt).get_center()
	var scaling := maxf(rules.minimum_scaling, 1.0 - combo * rules.combo_scaling_step)
	var damage := maxi(1, roundi(float(event.get("damage", 1)) * scaling))
	if not infinite_hp:
		damage = mini(damage, hp)
		hp -= damage
	combo += 1
	total_damage += damage
	if cinematic.active and move.category=="ultimate":
		cinematic.hits+=1;cinematic.damage+=damage
		if event.get("ultimate_finish",false):cinematic.finishing=true
	combo_damage += damage
	increment_ticks = 8
	if combo % 5 == 0: milestone_hits=combo;milestone_ticks=35
	if move.category in ["normal","assist"]: meter.gain(int(event.get("xp", 0)))
	dummy.motion.apply_event(event,int(context.facing))
	var impact_profile:=fx.profile_for(event)
	hitstop = maxi(hitstop, impact_profile.hitstop)
	if actor == 0:
		last_main = sim_tick
	else:
		last_assist = sim_tick
	if absi(last_main - last_assist) <= rules.cross_window and cross_cooldown == 0 and cross_count < rules.cross_limit_per_phase and not dummy.motion.knockdown and not cinematic.active:
		dummy.motion.suspend(rules.cross_suspend_ticks)
		cross_count += 1
		cross_cooldown = rules.cross_cooldown_ticks
		cross_text = 55
		if move.category in ["normal","assist"]: meter.gain(rules.overlap_meter_bonus)
		if effects_enabled: fx.cross_accent(contact)
	var at := contact
	if effects_enabled: fx.present_contact(at,damage,impact_profile,dummy,int(context.facing))
	presentation.accent(int(context.facing),impact_profile.camera_impulse)
	var record := {"token": token, "actor": actor, "sequence": move.sequence_id, "tick": sim_tick, "damage": damage, "contact": contact, "strike": strike, "hurt": hurt}
	hit_log.append(record)
	notify_action("CONTACT / " + move.display_name, true)
	if logging:
		print("HIT ", record)

func _on_cue(actor: int, event: Dictionary) -> void:
	var cue_actor:BattleActor=actors[actor] if actor<3 else cpu_actors[actor-3]
	if event.has("sound_event"):cue_actor.voice.play_event(str(event.sound_event))
	if cinematic.active and event.has("text"): cinematic.banner = str(event.text)
	if effects_enabled and event.has("camera"): fx.shake_left=maxf(fx.shake_left,float(event.camera)*.025)
	if effects_enabled and event.get("effect","")=="flash": fx.flash_left=maxf(fx.flash_left,.08)
	if event.get("sound","")=="hit": fx.play_impact_sound()
	if event.has("sound_layer"):
		fx.audio.enabled=fx.audio_enabled;fx.audio.play(str(event.sound_layer))
	if effects_enabled and event.get("effect", "") == "trail":
		fx.trails.append({"from": cue_actor.home, "to": cue_actor.position, "life": 0.0, "owner":scheduler.actions.get(actor,{}).get("id",-1)})

func _process(delta: float) -> void:
	for actor in actors+cpu_actors:
		actor.voice.enabled=fx.audio_enabled;actor.voice.advance(delta)
	var presentation_delta:=delta*(.25 if slow else 1.0)
	fx.advance(presentation_delta)
	weapon.density=fx.effect_density;weapon.reduced=cinematic.reduced
	weapon.advance(presentation_delta)
	backdrop.density=fx.effect_density;backdrop.advance(presentation_delta)
	presentation.advance(presentation_delta,world,fx.shake_strength)
	hud.queue_redraw()

func _exit_tree() -> void:
	if is_instance_valid(dummy):dummy.motion.end_capture(cinematic.action_id)
	cinematic.finish()
	if is_instance_valid(weapon):weapon.clear_all()
	if is_instance_valid(world):presentation.reset(world)
	if is_instance_valid(fx):fx.clear_all()

func _build_debug() -> void:
	debug_panel = PanelContainer.new()
	debug_panel.position = Vector2(785, 65)
	debug_panel.size = Vector2(465, 525)
	debug_panel.z_index = 100
	add_child(debug_panel)
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(465,510)
	debug_panel.add_child(scroll)
	var box := VBoxContainer.new()
	scroll.add_child(box)
	var title := Label.new()
	title.text = "F1 / ROSTER + TRAINING — apply at new battle"
	box.add_child(title)
	for slot in range(3):
		var picker := OptionButton.new()
		for data in definitions:
			picker.add_item(data.display_name+" ["+data.completion_status+"]")
		picker.selected = roles[slot]
		picker.item_selected.connect(func(index: int): stage_role(slot, index))
		role_pickers.append(picker)
		var row := HBoxContainer.new()
		box.add_child(row)
		var label := Label.new()
		label.text = ["Main    ", "Assist 1", "Assist 2"][slot]
		row.add_child(label)
		row.add_child(picker)
	for slot in range(2):
		var picker:=OptionButton.new()
		picker.item_selected.connect(func(index:int):pending_variants[slot]=index)
		variant_pickers.append(picker);box.add_child(picker)
	roster_status=Label.new();roster_status.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;roster_status.custom_minimum_size.x=360;box.add_child(roster_status)
	var apply:=Button.new();apply.text="Launch new battle with selected team";apply.pressed.connect(apply_team);box.add_child(apply)
	_refresh_selection()
	_toggle(box, "Roster versus CPU (applies on reset)", func(on:bool):versus_mode=on,versus_mode)
	_toggle(box, "Reduced flash / no target flashing", set_reduced_flash)
	_toggle(box, "Reduced ultimate camera", func(on: bool): cinematic.reduced = on)
	_toggle(box, "Short ultimate / 1.8x timeline (all beats)", func(on: bool): cinematic.shortened = on)
	_toggle(box, "Infinite player HP", func(on: bool): infinite_player_hp = on)
	_toggle(box, "Infinite target HP", func(on: bool): infinite_hp = on)
	_toggle(box, "Infinite meter / training", func(on: bool): infinite_meter = on)
	_toggle(box, "Hide impact effects (contact inspection)", func(on: bool): effects_enabled = not on)
	_toggle(box, "Slow motion / 25%", func(on: bool): slow = on)
	_toggle(box, "Hit-event logging", func(on: bool): logging = on)
	_toggle(box, "Hit / hurtbox display", func(on: bool):
		for actor in actors + [dummy]:
			actor.debug_boxes = on)
	_toggle(box, "Training / skip CPU offense (F6)", func(on: bool): ai_on = not on)
	var select := OptionButton.new()
	for phase_name in Phase.keys():
		select.add_item("Phase override: " + phase_name)
	select.item_selected.connect(_override_phase)
	box.add_child(select)
	for property_name in ["number_size", "shake_strength", "flash_strength", "effect_density"]:
		var slider := HSlider.new()
		slider.min_value = 0
		slider.max_value = 1.8 if property_name == "number_size" else 1
		slider.min_value = .6 if property_name == "number_size" else 0
		slider.step = 0.05
		slider.value = fx.get(property_name)
		slider.value_changed.connect(func(value: float): fx.set(property_name, value))
		var label := Label.new()
		label.text = property_name.replace("_", " ")
		box.add_child(label)
		box.add_child(slider)
	_toggle(box, "Mute generated impact audio", func(on: bool): fx.audio_enabled = not on)
	var button := Button.new()
	button.text = "Move preview / F2"
	button.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/MovePreview.tscn"))
	box.add_child(button)
	debug_panel.hide()

func set_reduced_flash(on: bool) -> void:
	fx.reduced_flash=on
	if on:
		fx.flash_left=0
		for actor in actors+[dummy]:actor.rim_left=0

func _toggle(box: VBoxContainer, title: String, callback: Callable, initial:bool=false) -> void:
	var button := CheckButton.new()
	button.text = title
	button.button_pressed=initial
	button.toggled.connect(callback)
	box.add_child(button)

func stage_role(slot:int,character_index:int)->void:
	if slot<0 or slot>2 or character_index<0 or character_index>=definitions.size():return
	var previous:=pending_roles[slot]
	var other:=pending_roles.find(character_index)
	pending_roles[slot]=character_index
	if other>=0 and other!=slot:pending_roles[other]=previous
	pending_variants=[0,0];_refresh_selection()
func _refresh_selection()->void:
	for i in range(3):role_pickers[i].select(pending_roles[i])
	for i in range(2):
		var picker:=variant_pickers[i];picker.clear()
		for path in definitions[pending_roles[i+1]].assist_variants:
			picker.add_item("Assist %d: " % (i+1)+(load(path) as SequenceData).display_name)
		if picker.item_count>0:picker.select(0)
	var data:=definitions[pending_roles[0]]
	roster_status.text=data.display_name+" — "+data.availability_note+"\nVoice: optional / missing clips are silent. Changes apply only on launch."
func apply_team()->void:
	for slot in range(3):
		if not definitions[pending_roles[slot]].supported_roles.has("main" if slot==0 else "assist"):
			notify_action("REJECTED / unsupported role",false);return
	roles.assign(pending_roles);assist_variants.assign(pending_variants)
	reset_match();debug_panel.hide();notify_action("NEW BATTLE / team applied",true)
func swap_role(slot:int,character_index:int)->void:
	# Explicit programmatic new-match helper, also used by regression tests.
	pending_roles.assign(roles);stage_role(slot,character_index);apply_team()

func _override_phase(index: int) -> void:
	# Overrides invalidate active attacks, buffers and pending motion before changing phase.
	reset_match()
	phase = index as Phase
	phase_ticks = 0
	if phase == Phase.PlayerAttackPhase:
		_begin_player_phase()
	elif phase == Phase.CPUAttackPhase:
		_begin_cpu_phase()
	elif phase == Phase.Reset:
		reset_match()

func _draw() -> void:
	# HUD stays above the world but below the debug panel via a separate draw node.
	pass

func meter_badge(slot:int)->String:
	var binding:=BattleCommands.label("ultimate" if slot==7 else "special_1" if slot==5 else "special_2")
	if move_path(slot).is_empty():return binding+" unavailable"
	var used:bool=ultimate_used if slot==7 else special_slots_used[slot-5]
	return binding+str(move_cost(slot))+" "+("used" if used else "ready" if meter.value>=move_cost(slot) else "charge")

func draw_hud(canvas: Node2D) -> void:
	var font := ThemeDB.fallback_font
	canvas.draw_rect(Rect2(0, 0, 1280, 58), Color("0e1928"))
	canvas.draw_string(font, Vector2(36, 145), "%02d" % combo, HORIZONTAL_ALIGNMENT_LEFT, -1, 76+increment_ticks, Color("fff0b7"))
	canvas.draw_string(font, Vector2(143, 135), "HITS", HORIZONTAL_ALIGNMENT_LEFT, -1, 27, Color("d9eff6"))
	canvas.draw_string(font, Vector2(40, 175), "%d COMBO DAMAGE" % combo_damage, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("bcd3dd"))
	var phase_name: String = ["MATCH INTRO", "PLAYER ATTACK PHASE", "PHASE RESOLUTION", "CPU ATTACK PHASE", "VICTORY / R TO REMATCH", "DEFEAT / R TO REMATCH", "RESET", "ULTIMATE / INPUT LOCKED"][phase]
	if phase == Phase.CPUAttackPhase:
		phase_name = "CPU / %s block / %s dodge" % [BattleCommands.label("cancel_block"),BattleCommands.label("dodge")]
	canvas.draw_rect(Rect2(365, 75, 550, 40), Color(0.05,0.10,0.17,0.9))
	canvas.draw_string(font, Vector2(385, 102), phase_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 21, Color("dfedf3"))
	canvas.draw_string(font, Vector2(385, 137), mode, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("ffb86b") if mode != "NORMAL" else Color("a0efdc"))
	if phase == Phase.CPUAttackPhase and scheduler.busy(3):
		var action: Dictionary = scheduler.actions[3]
		var upcoming := 0
		for event in action.move.hit_events:
			if int(event.tick) > int(action.tick):
				upcoming = int(event.tick)-int(action.tick)
				break
		canvas.draw_string(font,Vector2(390,170),"%s / IMPACT IN %.2fs" % [action.move.display_name,upcoming/60.0],HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color("ffd88c"))
	if defense_text_ticks > 0:
		canvas.draw_string(font,Vector2(440,235),defense_text,HORIZONTAL_ALIGNMENT_LEFT,-1,23,Color("95e6ff"))
	if cross_text > 0:
		canvas.draw_string(font, Vector2(480, 205), "CROSS HIT", HORIZONTAL_ALIGNMENT_LEFT, -1, 44, Color("ffe18b"))
	canvas.draw_string(font, Vector2(905, 142), ("CPU / "+definitions[cpu_team[0]].display_name if versus_mode else "CPU / PLACEHOLDER"), HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("edb9ab"))
	canvas.draw_rect(Rect2(905, 157, 330, 13), Color("382d37"))
	canvas.draw_rect(Rect2(905, 157, 330.0 * hp / rules.target_hp, 13), Color("f08b71"))
	canvas.draw_string(font, Vector2(905, 193), "%d / %d HP" % [hp, rules.target_hp], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("ffe8de"))
	canvas.draw_rect(Rect2(0, 610, 1280, 110), Color("0d1827"))
	canvas.draw_line(Vector2(0, 610), Vector2(1280, 610), Color("51798c"), 2)
	canvas.draw_string(font, Vector2(30, 642), definitions[roles[0]].display_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 25, Color("b4edff"))
	canvas.draw_rect(Rect2(30, 648, 300, 5), Color("69d7bf"))
	canvas.draw_string(font, Vector2(30, 677), "HP %d/%d   /   %d ACTIONS" % [player_hp,rules.target_hp if versus_mode else rules.player_hp,charges], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("c2dae3"))
	canvas.draw_string(font, Vector2(30, 697), (BattleCommands.label("attack") + " + arrows: sequence"), HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color("8aa4b8"))
	canvas.draw_string(font, Vector2(400, 642), BattleCommands.label("assist_1") + "  " + definitions[roles[1]].display_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 21, definitions[roles[1]].tint)
	canvas.draw_string(font, Vector2(400, 670), "USED" if assist_used[0] else "ASSIST READY", HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color("bcd3dd"))
	canvas.draw_string(font, Vector2(650, 642), BattleCommands.label("assist_2") + "  " + definitions[roles[2]].display_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 21, definitions[roles[2]].tint)
	canvas.draw_string(font, Vector2(650, 670), "USED" if assist_used[1] else "ASSIST READY", HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color("bcd3dd"))
	canvas.draw_string(font, Vector2(930, 641), "METER %d / %d" % [meter.value,meter.maximum], HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color("d9bdff"))
	canvas.draw_rect(Rect2(930, 657, 300, 10), Color("29364c"))
	canvas.draw_rect(Rect2(930, 657, 300.0 * meter.value/meter.maximum, 10), Color("b99dea"))
	for segment_x in [1030,1130]: canvas.draw_line(Vector2(segment_x,657),Vector2(segment_x,667),Color("0d1827"),2)
	canvas.draw_string(font,Vector2(930,696),meter_badge(5)+" | "+meter_badge(6)+" | "+meter_badge(7),HORIZONTAL_ALIGNMENT_LEFT,-1,14,Color("9eb2c4"))
	canvas.draw_string(font, Vector2(400, 697), "F2 move lab / F5 late / F6 CPU", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color("a6b7c4"))
	# Compact guide is built from the selected package and current InputMap.
	if phase!=Phase.CPUAttackPhase:
		var guide_x := 970 if dummy.home.x<640 else 25
		canvas.draw_rect(Rect2(guide_x,310,285,172),Color(.04,.08,.14,.82))
		var selectors := ["Neutral",BattleCommands.label("select_left"),BattleCommands.label("select_up"),BattleCommands.label("select_down"),BattleCommands.label("select_right")]
		for slot in range(5):
			canvas.draw_string(font,Vector2(guide_x+11,335+slot*25),"%s + %s: %s" % [selectors[slot],BattleCommands.label("attack"),move_name(slot).split(" / ")[0]],HORIZONTAL_ALIGNMENT_LEFT,260,14,Color("bdd9e9"))
		canvas.draw_string(font,Vector2(guide_x+11,470),"CANCEL %d | SPECIALS %d / %d | ULT %d" % [rules.cancel_cost,move_cost(5),move_cost(6),move_cost(7)],HORIZONTAL_ALIGNMENT_LEFT,270,12,Color("d4c1f4"))
	canvas.draw_rect(Rect2(25, 550, 1230, 42), Color(0.05,0.1,0.16,0.9))
	canvas.draw_string(font, Vector2(40, 578), feedback if feedback_ticks > 0 else "%s + direction: sequence | %s cancel (player) / block (CPU) | %s dodge" % [BattleCommands.label("attack"),BattleCommands.label("cancel_block"),BattleCommands.label("dodge")], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("a0efdc") if feedback_good else Color("ffc18f"))
	if milestone_ticks > 0:
		canvas.draw_string(font,Vector2(36,275),"%d HIT CHAIN" % milestone_hits,HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("a3efff"))
	if final_combo_ticks > 0 and combo == 0:
		canvas.draw_string(font,Vector2(36,275),"RESULT %d hits / %d damage" % [final_combo.x,final_combo.y],HORIZONTAL_ALIGNMENT_LEFT,-1,19,Color("ffe0a5"))
	var hint := "GRACE %.1fs" % (grace_left / 60.0)
	if scheduler.busy(0):
		var action: Dictionary = scheduler.actions[0]
		var move: SequenceData = action.move
		hint = "CHAIN NOW / direction + J" if action.tick >= move.chain_open else "CHAIN IN %.2fs" % (maxi(0, move.chain_open - int(action.tick)) / 60.0)
	if scheduler.busy(0):
		var a: Dictionary = scheduler.actions[0]
		hint += "  / CANCEL" if a.tick >= a.move.cancel_open and a.tick <= a.move.cancel_close else ""
	if cinematic.active: hint = "ULTIMATE ACTIVE"
	canvas.draw_string(font, Vector2(36, 217), hint, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("88e2de"))
	canvas.draw_string(font,Vector2(36,242),"QUEUE: " + (move_name(buffer_slot) if buffer_slot >= 0 else "empty"),HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color("dccaff"))
	if debug_panel.visible:
		canvas.draw_string(font, Vector2(35, 252), "Height %.1f | velocity %.1f | juggle %d | cross %df | stop %df" % [dummy.motion.height, dummy.motion.velocity, dummy.motion.juggle_hits, dummy.motion.cross_ticks, hitstop], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)
	if cinematic.active:
		canvas.draw_rect(Rect2(350,195,575,55),Color(.035,.08,.17,.92))
		canvas.draw_string(font,Vector2(365,220),cinematic.banner,HORIZONTAL_ALIGNMENT_LEFT,-1,23,Color("b4f0ff"))
		canvas.draw_string(font,Vector2(365,242),"PROTOTYPE CHOREOGRAPHY / "+str(cinematic.spec.get("motif","heavy energy")),HORIZONTAL_ALIGNMENT_LEFT,-1,13,Color("8eafca"))
		if cinematic.stage=="CONFIRM":
			var portrait:=actors[0].texture
			if portrait:
				canvas.draw_colored_polygon(PackedVector2Array([Vector2(760,190),Vector2(920,190),Vector2(905,330),Vector2(775,330)]),Color(.04,.12,.24,.96))
				canvas.draw_texture_rect_region(portrait,Rect2(780,195,120,125),actors[0].definition.portrait_region)
				canvas.draw_line(Vector2(760,190),Vector2(920,190),Color("83dfff"),2)
	if cinematic.summary_ticks>0:
		canvas.draw_string(font,Vector2(370,270),"ULTIMATE TOTAL: %d hits / %d damage (included in combo)" % [cinematic.summary.x,cinematic.summary.y],HORIZONTAL_ALIGNMENT_LEFT,-1,19,Color("b8ecff"))
	if dummy.motion.electrical_ticks>0:
		canvas.draw_string(font,Vector2(905,218),"ELECTRICAL %dt" % dummy.motion.electrical_ticks,HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color("c9b4ff"))
	if effects_enabled and not fx.reduced_flash and fx.flash_left > 0:
		canvas.draw_rect(Rect2(0, 240, 1280, 300), Color(1,0.92,0.7,fx.flash_left * fx.flash_strength * 1.7))

func mirror_setup() -> void:
	reset_match()
	phase = Phase.PlayerAttackPhase
	mode = "LEFT TRAINING"
	dummy.home.x = 390
	for i in range(3):
		actors[i].home.x = 965 + i * 70
		actors[i].opponent_x = dummy.home.x
		actors[i].facing = -1
		actors[i].sample({})
	dummy.sample({})
	notify_action("LEFT TEST / J attack; R restores right. F4 = out-of-range", true)

func miss_setup() -> void:
	reset_match()
	phase = Phase.PlayerAttackPhase
	mode = "MISS TEST"
	dummy.home.x = 1240
	dummy.sample({})
	notify_action("MISS TEST / J must cause no damage. R restores", true)

func contact_reason(strike: Rect2, hurt: Rect2) -> String:
	if hp <= 0: return "no valid target"
	if dummy.motion.knockdown or dummy.motion.recovery_ticks > 0: return "target invulnerable (knockdown recovery)"
	if not strike.has_area() or strike.end.x < hurt.position.x or strike.position.x > hurt.end.x:
		return "out of horizontal reach"
	if strike.end.y < hurt.position.y: return "target below strike region"
	if strike.position.y > hurt.end.y: return "target above strike region"
	return "CONTACT"

func _on_projectile_contact(shot: Dictionary, region: Rect2) -> void:
	if shot.actor>=3:
		_resolve_cpu_contact(shot.move,shot.event,shot.token,shot.actor,region);return
	_resolve_player_contact(shot.actor,shot.move,shot.event,shot.token,region,shot.context)
func _on_projectile_miss(shot: Dictionary, region: Rect2) -> void:
	if shot.actor>=3:return
	var reason := contact_reason(region,dummy.hurt_region())
	contact_log.append({"token":shot.token,"actor":shot.actor,"result":reason,"strike":region,"hurt":dummy.hurt_region(),"tick":sim_tick,
		"attacker":shot.context.position,"target":dummy.position,"target_elevation":dummy.elevation,"commit_tick":shot.context.commit_tick})
	notify_action("ARROW MISS / " + reason,false)

func _begin_cpu_phase() -> void:
	phase = Phase.CPUAttackPhase
	phase_ticks = 0
	defense.block(Input.is_action_pressed("cancel_block"))
	if ai_on and versus_mode:
		var data:=definitions[cpu_team[0]]
		# Decisions use a seeded random plan, never current defense input.
		var available:Array[String]=[]
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

		cpu_assists_left.assign([4,5]);cpu_wait=55
		notify_action("CPU TEAM / "+data.display_name+" + "+definitions[cpu_team[1]].display_name+" + "+definitions[cpu_team[2]].display_name,true)
	elif ai_on:
		var move: SequenceData = load("res://moves/cpu_%d.tres" % (cpu_round % 2))
		cpu_round += 1
		scheduler.start(3,move)
		AttackStaging.prepare(scheduler.actions[3],dummy,actors[0],false)
		notify_action("CPU WINDUP / hold SPACE or time SHIFT",true)

func _advance_roster_cpu()->void:
	if not ai_on:cpu_queue.clear();cpu_assists_left.clear();cpu_wait=0;return
	if player_hp<=0:cpu_queue.clear();cpu_assists_left.clear();cpu_wait=0;return
	if scheduler.busy(3):
		var at:int=scheduler.actions[3].tick
		if not cpu_assists_left.is_empty() and at>=(24 if cpu_assists_left.size()==2 else 58):
			var id:int=cpu_assists_left.pop_front()
			var move:SequenceData=load(definitions[cpu_team[id-3]].assist_sequence)
			scheduler.start(id,move);AttackStaging.prepare(scheduler.actions[id],cpu_actors[id-3],actors[0],false)
		return
	if not projectiles.shots.is_empty():return
	if cpu_wait>0:cpu_wait-=1;return
	if not cpu_queue.is_empty():
		var move:SequenceData=load(cpu_queue.pop_front())
		scheduler.start(3,move);AttackStaging.prepare(scheduler.actions[3],dummy,actors[0],false)
		cpu_wait=40
		notify_action("CPU / "+move.display_name+" — SPACE block / SHIFT dodge",true)

func _resolve_cpu_hit(move: SequenceData,event:Dictionary,token:String,actor:int=3)->void:
	if consumed.has(token):return
	var fighter:=cpu_actors[actor-3]
	fighter.sample(scheduler.actions.get(actor,{}));actors[0].sample({})
	if event.get("kind","melee")=="projectile":
		var context:Dictionary={"position":fighter.position,"facing":fighter.facing,"aim":actors[0].position+Vector2(0,-90-actors[0].elevation)}
		projectiles.fire(actor,move,event,token,fighter,context);return
	_resolve_cpu_contact(move,event,token,actor,fighter.strike_region(event))

func _resolve_cpu_contact(move:SequenceData,event:Dictionary,token:String,actor:int,region:Rect2)->void:
	if consumed.has(token) or player_hp<=0:return
	var hurt:=actors[0].hurt_region()
	if not region.intersects(hurt):return
	consumed[token]=true
	var result:=defense.resolve(int(event.damage))
	if not infinite_player_hp:player_hp=maxi(0,player_hp-int(result.damage))
	actors[0].defeated=player_hp<=0
	if int(result.damage)>0:actors[0].voice.play_event("defeat" if player_hp<=0 else "hurt")
	var at:=region.intersection(hurt).get_center()
	if result.label in ["PERFECT BLOCK","DODGE"]:meter.gain(rules.defense_meter_bonus)
	defense_text=result.label;defense_text_ticks=45
	if int(result.damage)>0:
		cpu_meter=mini(300,cpu_meter+int(event.get("xp",0)))
		actors[0].motion.apply_event(event,cpu_actors[actor-3].facing)
		if effects_enabled:fx.present_contact(at,int(result.damage),fx.profile_for(event),actors[0],cpu_actors[actor-3].facing)
	hitstop=int(event.get("hitstop",3))
	cpu_log.append({"token":token,"actor":actor,"sequence":move.sequence_id,"tick":sim_tick,"damage":result.damage,"result":result.label,"contact":at,"strike":region,"hurt":hurt})
	notify_action(result.label,true)

func late_setup() -> void:
	reset_match()
	phase = Phase.PlayerAttackPhase
	request_main(2)
	for i in range(80): simulate_tick()
	fx.clear_all()
	mode = "LATE ASSIST TEST / knee may connect; committed heel passes above"
	request_assist(2)
