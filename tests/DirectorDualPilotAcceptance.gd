extends SceneTree
## F2-only Director pilot validation: real scheduler, projectile system and hurtboxes.
var checks: int = 0
var failures: int = 0
const PILOTS: Array[Dictionary] = [
	{"file":"res://moves/director_drafts/dante_blade_gun_break_preview.tres",
	 "fighter":"dante","duration":182,"pose_count":19,"hit_count":6,
	 "projectiles":2},
	{"file":"res://moves/director_drafts/kosmos_heavy_break_preview.tres",
	 "fighter":"kosmos","duration":173,"pose_count":16,"hit_count":6,
	 "projectiles":0},
]

func ok(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures += 1
	print(("PASS " if condition else "FAIL ") + label)

func _initialize() -> void:
	run.call_deferred()

func run() -> void:
	var d: BattleDemo = load("res://scenes/BattleDemo.tscn").instantiate()
	root.add_child(d)
	d.versus_mode = false
	d.preview_only = true
	d.ai_on = false
	d.set_process(false)
	d.set_physics_process(false)
	d.fx.audio_enabled = false
	d.infinite_hp = true
	for spec in PILOTS:
		var file: String = spec.file
		var move: SequenceData = load(file)
		ok(move != null, "loads " + file)
		if move == null:
			continue
		ok(move.sequence_id.begins_with("director_"), "sandbox sequence id")
		ok(move.character == spec.fighter and move.category == "normal", "pilot identity")
		ok(move.duration_ticks == spec.duration and move.duration_ticks >= 120 and move.duration_ticks <= 300,
			"2–5 second regular attack duration " + spec.fighter)
		ok(move.poses.size() == spec.pose_count and move.hit_events.size() == spec.hit_count, "pose and hit counts")
		var total: int = 0
		for pose in move.poses:
			total += int(pose.ticks)
			ok(ResourceLoader.exists(str(pose.path)), "real sprite " + str(pose.path))
		ok(total == move.duration_ticks, "pose timeline budget")
		var projectiles: int = 0
		var ids: Array[String] = []
		for event in move.hit_events:
			if event.get("kind", "melee") == "projectile":
				projectiles += 1
			ids.append(str(event.id))
		ok(projectiles == spec.projectiles, "ranged identity count")
		ok(ids.size() == ids.duplicate().size(), "hit event ids preserved")
		var actor_index: int = -1
		for j in range(d.definitions.size()):
			if d.definitions[j].character_id == spec.fighter:
				actor_index = j
			ok(not d.definitions[j].main_sequences.has(file)
				and not d.definitions[j].special_sequences.has(file)
				and d.definitions[j].ultimate_sequence != file,
				"preview not in playable roster: " + d.definitions[j].character_id)
		ok(actor_index >= 0, "character present in roster")
		if actor_index < 0:
			continue
		for mirrored in [false, true]:
			d.roles.assign([actor_index, 1, 2])
			if mirrored:
				d.mirror_setup()
			else:
				d.reset_match()
				d.phase = BattleDemo.Phase.PlayerAttackPhase
			d.infinite_hp = true
			d.ai_on = false
			ok(d.scheduler.start(0, move), "scheduler started: " + spec.fighter + " left=" + str(mirrored))
			if not d.scheduler.actions.has(0):
				continue
			AttackStaging.prepare(d.scheduler.actions[0], d.actors[0], d.dummy, false)
			for i in range(move.duration_ticks + 220):
				d.simulate_tick()
				d._process(1.0/60.0)
			var confirmed: Array[String] = []
			for accepted in d.hit_log:
				if str(accepted.get("sequence", "")) == move.sequence_id:
					confirmed.append(str(accepted.get("token", "")).split(":")[-1])
			for event in move.hit_events:
				if confirmed.has(str(event.id)):
					continue
				var attempts: Array[String] = []
				for item in d.contact_log:
					if str(item.get("token", "")).ends_with(":" + str(event.id)):
						attempts.append("%s strike=%s hurt=%s attacker=%s target=%s" % [
							str(item.get("result", "")), str(item.get("strike", "")),
							str(item.get("hurt", "")), str(item.get("attacker", "")),
							str(item.get("target", ""))])
				print("DIRECTOR PILOT MISS ", spec.fighter, " mirrored=", mirrored,
					" event=", event.id, " attempts=", attempts)
			ok(confirmed.size() == move.hit_events.size(),
				"all authentic events contacted " + spec.fighter +
				" mirrored=" + str(mirrored) + " count=" + str(confirmed.size()))
			var real_intersection: bool = true
			for accepted in d.hit_log:
				if str(accepted.get("sequence", "")) != move.sequence_id:
					continue
				real_intersection = real_intersection and accepted.strike.has_point(accepted.contact) \
					and accepted.hurt.has_point(accepted.contact)
			ok(real_intersection, "real hurtbox/strike intersection")
			ok(d.scheduler.actions.is_empty() and d.projectiles.shots.is_empty()
				and not d.cinematic.active, "no orphan action/projectile/cinematic")
			d.reset_match()
			d.roles.assign([actor_index, 1, 2])
			d.phase = BattleDemo.Phase.PlayerAttackPhase
			d.scheduler.start(0, move)
			AttackStaging.prepare(d.scheduler.actions[0], d.actors[0], d.dummy, false)
			for i in range(15):
				d.simulate_tick()
			d.reset_match()
			ok(d.scheduler.actions.is_empty() and d.projectiles.shots.is_empty()
				and d.hit_log.is_empty(), "mid-move reset clears ownership")
	print("DIRECTOR DANTE/KOSMOS PILOTS: %d checks / %d failures" % [checks, failures])
	d.queue_free()
	await process_frame
	quit(1 if failures else 0)
