extends BattleDemo
## Preview uses the same scheduler and hit resolver, never a second damage path.
var selected_move: SequenceData
var move_paths: Array[String] = ["res://moves/kosmos_arc.tres","res://moves/kosmos_barrage.tres","res://moves/kosmos_up.tres","res://moves/kosmos_down.tres","res://moves/kosmos_right.tres","res://moves/chunli_assist.tres","res://moves/xiaoyu_assist.tres","res://moves/kosmos_assist.tres","res://moves/kosmos_special_1.tres","res://moves/kosmos_special_2.tres","res://moves/kosmos_ultimate.tres"]
var preview_offset:=Vector2.ZERO
var running: bool = false
var preview_rate: float = 1.0
var preview_accumulator: float = 0.0
var track: Node2D
var info: Label
var steps: int = 0

func _ready() -> void:
	preview_only = true
	super._ready()
	infinite_hp = true
	for data in definitions:
		var paths:Array[String]=[]
		paths.append_array(data.main_sequences);paths.append_array(data.special_sequences);paths.append_array(data.assist_variants);paths.append(data.ultimate_sequence)
		for path in paths:
			if not path.is_empty() and not move_paths.has(path):move_paths.append(path)
	# Director-only sandbox move: visible in F2 Move Preview, not the playable roster.
	var director_preview := "res://moves/director_drafts/chunli_neutral_b_preview.tres"
	if ResourceLoader.exists(director_preview) and not move_paths.has(director_preview):
		move_paths.append(director_preview)
	var director_baseline := "res://moves/director_drafts/chunli_neutral_b_baseline.tres"
	if ResourceLoader.exists(director_baseline) and not move_paths.has(director_baseline):
		move_paths.append(director_baseline)
	var panel := PanelContainer.new()
	panel.position = Vector2(25, 270)
	panel.size = Vector2(310, 270)
	panel.z_index = 80
	add_child(panel)
	var box := VBoxContainer.new()
	panel.add_child(box)
	info = Label.new()
	box.add_child(info)
	var selector := OptionButton.new()
	for path in move_paths:
		var move: SequenceData = load(path)
		selector.add_item(move.display_name)
	selector.item_selected.connect(func(index: int): select_move(index))
	box.add_child(selector)
	var row := HBoxContainer.new()
	box.add_child(row)
	for title in ["Replay", "Play/pause", "+1 tick", "Next pose"]:
		var button := Button.new()
		button.text = title
		row.add_child(button)
		match title:
			"Replay": button.pressed.connect(replay)
			"Play/pause": button.pressed.connect(func(): running = not running)
			"+1 tick": button.pressed.connect(func(): running = false; step_preview())
			"Next pose": button.pressed.connect(next_pose)
	var speed := OptionButton.new()
	for name_text in ["Full speed / 60 ticks per second", "Slow motion / 25%"]:
		speed.add_item(name_text)
	speed.item_selected.connect(func(index: int): preview_rate = 1.0 if index == 0 else 0.25)
	box.add_child(speed)
	for axis in range(2):
		var offset_row := HBoxContainer.new()
		box.add_child(offset_row)
		var label := Label.new()
		label.text = "Preview offset " + ("X" if axis == 0 else "Y")
		offset_row.add_child(label)
		var spin := SpinBox.new()
		spin.min_value = -200
		spin.max_value = 200
		spin.step = 1
		spin.value_changed.connect(func(value: float): preview_offset[axis] = value; actors[0].pose_offset[axis] = value)
		offset_row.add_child(spin)
	var copy := Button.new()
	copy.text = "Copy offset JSON for choreography manifest"
	copy.pressed.connect(func(): DisplayServer.clipboard_set(JSON.stringify({"offset": [actors[0].pose_offset.x, actors[0].pose_offset.y]})))
	box.add_child(copy)
	var back := Button.new()
	back.text = "Return to battle / " + BattleCommands.label("preview_return")
	back.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/BattleDemo.tscn"))
	box.add_child(back)
	track = Node2D.new()
	track.z_index = 70
	track.draw.connect(_draw_track)
	add_child(track)
	select_move(0)

func select_move(index: int) -> void:
	selected_move = load(move_paths[index])
	replay()
	running = false

func replay() -> void:
	reset_match()
	phase = Phase.PlayerAttackPhase
	var definition := definitions[0]
	for candidate in definitions:
		if candidate.character_id == selected_move.character:
			definition = candidate
	actors[0].configure(definition, Vector2(315, 520))
	actors[0].pose_offset=preview_offset
	scheduler.start(0, selected_move)
	AttackStaging.prepare(scheduler.actions[0],actors[0],dummy,false)
	if selected_move.category=="ultimate":
		cinematic.begin(int(scheduler.actions[0].id),selected_move,definition);phase=Phase.Ultimate
		presentation.claim("ultimate",100);weapon.active=cinematic.beam_presentation
	actors[0].sample(scheduler.actions[0])
	steps = 0
	running = true

func step_preview() -> void:
	if scheduler.actions.is_empty() and projectiles.shots.is_empty() and dummy.motion.settled():
		running = false
		return
	# Preview advances the authored timeline, including hitstop ticks separately.
	simulate_tick()
	if not running:super._process(1.0/60)
	steps += 1
	info.text = "MOVE LAB / pose %d / sim tick %d" % [actors[0].pose_index, steps]
	track.queue_redraw()

func next_pose() -> void:
	running = false
	var before := actors[0].pose_index
	for i in range(180):
		step_preview()
		if actors[0].pose_index != before or scheduler.actions.is_empty():
			break

func _process(delta: float) -> void:
	if running:super._process(delta*preview_rate)
	else:hud.queue_redraw()

func _physics_process(_delta: float) -> void:
	if running:
		preview_accumulator += preview_rate
		while preview_accumulator >= 1:
			preview_accumulator -= 1
			step_preview()

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.echo: return
	if event.is_action_pressed("preview_return"): get_tree().change_scene_to_file("res://scenes/BattleDemo.tscn")
	elif event.is_action_pressed("reset_match"): replay()
	elif event.is_action_pressed("preview_step"): running=false;step_preview()
	elif event.is_action_pressed("preview_pause"): running=not running

func _draw_track() -> void:
	if selected_move == null:
		return
	track.draw_rect(Rect2(360, 245, 865, 45), Color("122334"))
	track.draw_line(Vector2(380, 270), Vector2(1200, 270), Color("7599ac"), 3)
	for event in selected_move.hit_events:
		var x := 380 + 820.0 * float(event.tick) / selected_move.duration_ticks
		track.draw_line(Vector2(x, 249), Vector2(x, 282), Color("ffbc6d"), 3)
	var current := selected_move.duration_ticks
	if scheduler.busy(0):
		current = scheduler.actions[0].tick
	var cursor_x := 380 + 820.0 * current / selected_move.duration_ticks
	track.draw_circle(Vector2(cursor_x, 270), 6, Color("80f2dc"))
