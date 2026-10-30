extends SceneTree
func _initialize() -> void: run.call_deferred()
func run() -> void:
	var d: BattleDemo=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.preview_only=true;d.fx.audio_enabled=false
	for left in [false,true]:
		for slot in range(8):
			if left:d.mirror_setup()
			else:d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase
			d.meter.value=300
			d.request_main(slot)
			for i in range(320):d.simulate_tick()
			print("PROBE ",left," slot ",slot," hits ",d.hit_log.size()," contacts ",d.hit_log," wall ",d.dummy.motion.wall_events)
	d.queue_free();await process_frame;quit()
