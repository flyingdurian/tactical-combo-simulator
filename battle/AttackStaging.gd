class_name AttackStaging
extends RefCounted
## One resolved entry, bounded alignment until commitment, never post-strike homing.
static func prepare(action: Dictionary, fighter: BattleActor, target: BattleActor, miss_mode: bool) -> void:
	var move: SequenceData = action.move
	if move.staging.is_empty(): return
	var spec := move.staging
	var facing := int(action.get("entry_facing", 1 if (target.home.x + target.motion.displacement) >= fighter.home.x else -1))
	var contact_x := clampf((target.home.x + target.motion.displacement) - facing * float(spec.get("distance", 95)), 180, 1070)
	if miss_mode: contact_x = minf(contact_x, 650)
	var current_x := fighter.position.x
	var entry_x := contact_x - facing * float(spec.get("entry_offset", 150)) if move.role == "assist" else current_x
	var max_correction := float(spec.get("max_correction", 600))
	contact_x = clampf(contact_x, entry_x - max_correction, entry_x + max_correction)
	action.stage = {"entry": Vector2(entry_x, 520), "contact": Vector2(contact_x, 520), "return": fighter.home + Vector2(fighter.motion.displacement, 0),
		"facing": facing, "elevation": clampf((target.motion.height + clampf(target.motion.velocity * float(spec.get("anticipate_rise_ticks",0))/60,0,32)) * float(spec.get("height_ratio", 0.8)), 0, float(spec.get("max_elevation", 130))),
		"aim": Vector2(target.home.x + target.motion.displacement, 430-target.motion.height-clampf(target.motion.velocity*.15,-35,35)), "initial_x": contact_x, "committed": false, "commit_tick": -1, "miss_mode": miss_mode}

static func advance_segments(action: Dictionary, fighter: BattleActor, target: BattleActor) -> void:
	if not action.has("stage"): return
	for segment in action.move.staging.get("segments",[]):
		var at_tick := int(segment.tick)
		if int(action.tick) < at_tick or int(action.stage.get("segment_tick",-1)) >= at_tick: continue
		var stage: Dictionary = action.stage
		stage.segment_tick = at_tick
		stage.entry = fighter.position
		stage.entry_elevation = fighter.elevation
		stage.contact = Vector2(clampf(target.home.x+target.motion.displacement-int(stage.facing)*float(segment.distance),180,1070),520)
		if stage.miss_mode: stage.contact.x = minf(stage.contact.x,650)
		stage.elevation = clampf(target.motion.height*float(segment.get("height_ratio",0)),0,140)
		stage.aim = Vector2(target.home.x+target.motion.displacement,430-target.motion.height-clampf(target.motion.velocity*.15,-35,35))
		stage.approach_start = at_tick
		stage.approach_end = at_tick+int(segment.get("approach_ticks",14))
		# Each inter-stage dash commits to a snapshot; no unlimited tracking.
		stage.committed = true
		stage.commit_tick = at_tick

static func align(action: Dictionary, target: BattleActor) -> void:
	if not action.has("stage"): return
	var spec: Dictionary = action.move.staging
	var stage: Dictionary = action.stage
	if stage.committed: return
	var desired := (target.home.x + target.motion.displacement) - int(stage.facing) * float(spec.get("distance", 95))
	var limit := float(spec.get("alignment_limit", 24))
	if not stage.miss_mode:
		stage.contact.x = clampf(desired, float(stage.initial_x)-limit, float(stage.initial_x)+limit)
	# Elevation chosen on entry is intentional: a late aerial call may pass above a falling target.
	if int(action.tick) >= int(spec.get("commit_tick", 12)):
		stage.committed = true
		stage.commit_tick = int(action.tick)

static func placement(action: Dictionary) -> Dictionary:
	var spec: Dictionary = action.move.staging
	var stage: Dictionary = action.stage
	var tick := float(action.tick)
	var approach_start := float(stage.get("approach_start",spec.get("approach_start", 4)))
	var approach_end := float(stage.get("approach_end",spec.get("approach_end", 14)))
	var weight := clampf((tick - approach_start)/maxf(1, approach_end-approach_start), 0, 1)
	weight = 1-pow(1-weight, 3)
	var at: Vector2 = stage.entry.lerp(stage.contact, weight)
	var elevation := lerpf(float(stage.get("entry_elevation",0)),float(stage.elevation),weight)
	var exit_start := float(spec.get("exit_start", 50))
	var exit_end := float(spec.get("exit_end", action.move.duration_ticks))
	if tick >= exit_start:
		var exit_weight := smoothstep(exit_start, exit_end, tick)
		var end: Vector2 = stage.contact - Vector2(int(stage.facing)*float(spec.get("entry_offset", 150)), 0) if action.move.role == "assist" else stage.return
		at = stage.contact.lerp(end, exit_weight)
		elevation *= 1-exit_weight
	return {"position": at, "elevation": elevation}
