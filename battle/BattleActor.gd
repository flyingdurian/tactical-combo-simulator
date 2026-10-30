class_name BattleActor
extends Node2D
## Presentation is sampled by timeline tick; never signals gameplay completion.
var voice:CharacterVoice
var defeated:bool=false
var rim_left: int = 0
var rim_color: Color = Color.WHITE
var rim_strength: float = .3
var definition: CharacterDefinition
var home: Vector2
var motion := TargetMotion.new()
var pose_offset := Vector2.ZERO
var debug_boxes: bool = false
var missing_art: bool = false
var acting: bool = false
var target_dummy: bool = false
var tint := Color.WHITE
var cache: Dictionary = {}
var texture: Texture2D
var pose_anchors: Dictionary = {}
var pose_index: int = 0
var visual_tick: int = 0
var authored_offset := Vector2.ZERO
var debug_reach: float = 0
# Root stays on the arena floor. Elevation and art offsets never move gameplay roots.
var elevation: float = 0
var facing: int = 1
var native_facing: int = 1
var opponent_x: float = 890
var action_id: int = -1
var frame_anchor := Vector2(128, 176)
var cosmetic_dodge: bool = false
var visual_attack_direction: int = 1
var release_ticks: int = 0
var release_position := Vector2.ZERO
var release_height: float = 0
var active_regions: Array[Rect2] = []

func _ready()->void:
	voice=CharacterVoice.new();add_child(voice)

func hurt_region() -> Rect2:
	return Rect2(position + definition.hurtbox.position - Vector2(0,elevation),definition.hurtbox.size)

func strike_region(event: Dictionary) -> Rect2:
	var box: Array = event.get("region", [])
	if box.size() != 4:
		return Rect2()
	var x := float(box[0]) if facing > 0 else -float(box[0]) - float(box[2])
	return Rect2(position + Vector2(x, float(box[1]) - elevation), Vector2(float(box[2]), float(box[3])))

func configure(data: CharacterDefinition, at: Vector2) -> void:
	definition = data
	defeated=false;pose_offset=Vector2.ZERO;authored_offset=Vector2.ZERO;pose_anchors.clear();release_ticks=0
	if voice:voice.configure(data.sound_profile)
	home = at
	position = home
	action_id = -1
	facing = 1
	elevation = 0
	tint = definition.tint
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	set_image(definition.idle_texture)

func set_image(path: String) -> void:
	if path.is_empty():
		texture = null
		missing_art = not target_dummy
		return
	if not cache.has(path):
		cache[path] = load(path) if ResourceLoader.exists(path) else null
	texture = cache[path]
	missing_art = texture == null

func release_action() -> void:
	release_ticks = 12
	release_position = position
	release_height = elevation
func advance_release() -> void:
	rim_left=maxi(0,rim_left-1)
	release_ticks = maxi(0, release_ticks - 1)
func sample(action: Dictionary) -> void:
	acting = not action.is_empty()
	debug_reach = 0
	active_regions.clear()
	pose_anchors = definition.anchors.duplicate(true)
	frame_anchor = definition.pivot
	native_facing = definition.native_facing
	var travel := Vector2.ZERO
	var image_path: String = definition.idle_texture
	if not acting and motion.stun_ticks > 0 and not definition.hurt_texture.is_empty():
		image_path = definition.hurt_texture
	if defeated and not definition.defeat_texture.is_empty():image_path=definition.defeat_texture
	elif not acting and motion.recovery_ticks>0 and not definition.recovery_texture.is_empty():image_path=definition.recovery_texture
	pose_index = 0
	authored_offset = Vector2.ZERO
	if acting:
		release_ticks = 0
		var move: SequenceData = action.move
		if action_id != int(action.id):
			action_id = int(action.id)
			facing = int(action.stage.facing) if action.has("stage") else (1 if opponent_x >= home.x else -1)
		debug_reach = move.reach
		visual_tick = int(action.tick)
		var remaining := visual_tick
		for i in range(move.poses.size()):
			var pose: Dictionary = move.poses[i]
			pose_index = i
			pose_anchors.merge(pose.get("anchors", {}), true)
			var anchor: Array = pose.get("anchor", [128, 176])
			frame_anchor = Vector2(float(anchor[0]), float(anchor[1]))
			native_facing = int(pose.get("native_facing", native_facing))
			visual_attack_direction = int(pose.get("attack_direction", native_facing))
			image_path = str(pose.get("path", ""))
			var offset_data: Array = pose.get("offset", [0, 0])
			authored_offset = Vector2(float(offset_data[0]), float(offset_data[1]))
			remaining -= maxi(1, int(pose.get("ticks", 1)))
			if remaining < 0:
				break
		for i in range(move.movement.size()):
			var point: Dictionary = move.movement[i]
			if visual_tick >= int(point.tick):
				travel = Vector2(float(point.get("x", 0)), float(point.get("y", 0)))
				if i + 1 < move.movement.size():
					var next: Dictionary = move.movement[i + 1]
					var weight := clampf(float(visual_tick - int(point.tick)) / maxf(1, float(next.tick) - float(point.tick)), 0, 1)
					weight = 1.0 - pow(1.0 - weight, 3.0) if point.get("ease", "") == "out" else weight
					travel = travel.lerp(Vector2(float(next.get("x", 0)), float(next.get("y", 0))), weight)
	set_image(image_path)
	position = home + Vector2(travel.x * facing + motion.displacement + motion.recoil_x(), 0)
	elevation = maxf(0, -travel.y) + motion.height
	if acting and action.has("stage"):
		var placement := AttackStaging.placement(action)
		position = placement.position + Vector2(travel.x*facing,0)
		elevation = placement.elevation + maxf(0,-travel.y) + motion.height
	if not acting and release_ticks > 0:
		var weight := smoothstep(0, 12, 12-release_ticks)
		position = release_position.lerp(home + Vector2(motion.displacement,0),weight)
		elevation = lerpf(release_height,motion.height,weight)
	# Brief fade only at assist entry/exit; logical contact remains unchanged.
	modulate.a = 1.0
	if acting and action.move.role == "assist":
		modulate.a = minf(clampf(float(action.tick)/4, 0, 1), clampf(float(action.move.duration_ticks-action.tick)/6,0,1))
	if acting:
		for event in action.move.hit_events:
			if visual_tick >= int(event.tick) and visual_tick <= int(event.get("end_tick", event.tick)):
				active_regions.append(strike_region(event))
	queue_redraw()

func _draw() -> void:
	var font := ThemeDB.fallback_font
	# The shadow is always ground-relative, including during launch/Cross Hit.
	draw_set_transform(Vector2.ZERO, 0, Vector2(1, 0.22))
	draw_circle(Vector2.ZERO, 36, Color(0.02, 0.04, 0.07, 0.5))
	draw_set_transform(Vector2(0, -elevation))
	if target_dummy:
		draw_set_transform(Vector2(0,-elevation),clampf(-motion.horizontal_velocity*.002,-.12,.12)+motion.recoil_direction*motion.recoil_tilt*motion.recoil_weight(),Vector2(1+motion.recoil_squash*motion.recoil_weight(),1-motion.recoil_squash*motion.recoil_weight()))
		if motion.knockdown and elevation == 0:
			draw_set_transform(Vector2(0,-24),PI/2,Vector2(.8,.8))
		var body_color := Color("fa806d").lerp(rim_color,rim_strength if rim_left>0 else 0.0)
		draw_rect(Rect2(-35, -142, 70, 110), body_color)
		draw_rect(Rect2(-27, -176, 54, 32), Color("324152"))
		draw_rect(Rect2(-18, -166, 36, 7), Color("76f7ed"))
		draw_line(Vector2(-21, -32), Vector2(-26, 0), body_color, 14)
		draw_line(Vector2(21, -32), Vector2(26, 0), body_color, 14)
		if acting:
			var fist := Vector2(facing*96,-109) if not active_regions.is_empty() else Vector2(-facing*20,-125)
			draw_line(Vector2(facing*23,-112),fist,body_color,15)
			draw_circle(fist,12,Color("fff0b7"))
		draw_set_transform(Vector2(0,-elevation))
		# Identity is labeled in the HUD; keep the contact area free of duplicate text.
	elif texture != null:
		var tilt:=motion.recoil_direction*motion.recoil_tilt*motion.recoil_weight()
		if defeated and definition.defeat_texture.is_empty():tilt=facing*.8
		draw_set_transform(Vector2(-facing*24 if cosmetic_dodge else 0, -elevation), tilt, Vector2(facing * native_facing, 1))
		draw_texture_rect(texture, Rect2(-frame_anchor * definition.sprite_scale + pose_offset + authored_offset, texture.get_size() * definition.sprite_scale), false, Color(.55,.58,.65) if defeated else Color.WHITE.lerp(rim_color,rim_strength if rim_left>0 else 0.0))
		draw_set_transform(Vector2(0, -elevation))
	else:
		# Explicit geometric stand-in, not a sprite claimed to be this character.
		var lean := sin(visual_tick * 0.23) * 10.0 if acting else 0.0
		draw_circle(Vector2(lean, -136), 16, tint.lightened(0.35))
		draw_colored_polygon(PackedVector2Array([Vector2(-19+lean,-113),Vector2(18+lean,-113),Vector2(27,-62),Vector2(-24,-62)]), tint)
		draw_line(Vector2(-12, -62), Vector2(-24, 0), tint, 13)
		var kick := Vector2(82, -76) if acting and (visual_tick / 5) % 2 == 0 else Vector2(25, 0)
		draw_line(Vector2(12, -62), kick, tint.lightened(0.18), 13)
		draw_line(Vector2(15+lean, -105), Vector2(55+lean, -88), tint, 10)
		draw_string(font, Vector2(-75, -175), definition.display_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, tint.lightened(0.2))
		draw_string(font, Vector2(-72, -156), "MISSING SHEET", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color.WHITE)
	if motion.cross_ticks > 0:
		draw_arc(Vector2(0, -90), 74, 0, TAU, 40, Color("ffe795"), 2)
		for side in [-1,1]: draw_line(Vector2(-32,-90-side*32),Vector2(32,-90+side*32),Color(1,.9,.55,.6),2)
	draw_set_transform(Vector2.ZERO)
	if debug_boxes:
		for region in active_regions:
			draw_rect(Rect2(region.position - position, region.size), Color("ffd788"), false, 2)
		var hurt := hurt_region()
		draw_rect(Rect2(hurt.position - position, hurt.size), Color("8afed3"), false, 2)
		draw_circle(Vector2.ZERO, 5, Color.YELLOW)
		draw_circle(Vector2(0, -elevation), 3, Color.CYAN)
		draw_line(Vector2(0, -190-elevation), Vector2(facing*45, -190-elevation), Color.CYAN, 3)
		draw_string(font, Vector2(-25, 27), "F %d" % facing, HORIZONTAL_ALIGNMENT_LEFT, -1, 12)
		# Distinct arrows: intended / corrected visual attack / hitbox / target direction.
		for item in [[-225, facing, Color.CYAN], [-215, facing*native_facing*visual_attack_direction, Color.MAGENTA], [-205, facing, Color.YELLOW], [-195, signf(opponent_x-position.x), Color.GREEN]]:
			var at := Vector2(0, float(item[0])-elevation)
			var tip := at + Vector2(float(item[1])*45,0)
			draw_line(at,tip,item[2],2)
			draw_line(tip,tip+Vector2(-float(item[1])*8,-4),item[2],2)
		var origin := Vector2(-frame_anchor.x*definition.sprite_scale*facing*native_facing, -frame_anchor.y*definition.sprite_scale-elevation)
		draw_circle(origin,3,Color.MAGENTA)

# Source-pixel anchors use precisely the same transform as the displayed pose.
func anchor_world(key: String, fallback: Vector2 = Vector2.ZERO) -> Vector2:
	if not pose_anchors.has(key):return position+Vector2(fallback.x*facing,fallback.y-elevation)
	var xy: Array=pose_anchors[key]
	var local: Vector2=(Vector2(xy[0],xy[1])-frame_anchor)*definition.sprite_scale+pose_offset+authored_offset
	local.x*=facing*native_facing
	return position+local-Vector2(0,elevation)
