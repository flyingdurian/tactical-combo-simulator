extends SceneTree
func _initialize() -> void:run.call_deferred()
func run() -> void:
	var d: BattleDemo=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.preview_only=true;d.set_process(false);d.fx.audio_enabled=false
	for pair in [[0,1,"light"],[3,3,"heavy"],[5,3,"energy"],[6,3,"electrical"]]:
		d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase;d.meter.value=300;d.request_main(pair[0])
		for i in range(250):
			d.simulate_tick();d._process(1.0/60)
			if d.hit_log.size()>=pair[1]:
				await process_frame;await RenderingServer.frame_post_draw
				root.get_texture().get_image().save_png("res://docs/ImpactA_%s.png" % pair[2]);break
		print("PROFILE DEMO ",pair[2]," hits=",d.hit_log.size()," effects=",d.fx.contact_effects)
	d.queue_free();await process_frame;quit()
