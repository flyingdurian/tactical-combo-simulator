extends SceneTree
func _initialize() -> void: run.call_deferred()
func run() -> void:
	var preview=load("res://scenes/MovePreview.tscn").instantiate()
	root.add_child(preview)
	preview.fx.audio_enabled=false
	for index in range(preview.move_paths.size()):
		preview.select_move(index)
		preview.running=false
		for i in range(650):preview.step_preview()
		if not preview.scheduler.actions.is_empty() or not preview.projectiles.shots.is_empty():
			push_error("Preview failed to resolve %d" % index);quit(1);return
	preview.queue_free();await process_frame
	print("PREVIEW SMOKE: all 11 player move selections resolved")
	quit()
