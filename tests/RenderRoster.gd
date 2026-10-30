extends SceneTree
func _initialize()->void:run.call_deferred()
func run()->void:
	var d:BattleDemo=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.versus_mode=false;d.preview_only=true;d.set_process(false);d.set_physics_process(false);d.fx.audio_enabled=false
	DirAccess.make_dir_recursive_absolute("res://docs/roster16_contacts")
	for cid in range(6,16):
		for slot in [0,1,3]:
			d.roles.assign([cid,1 if cid!=1 else 0,2 if cid!=2 else 0]);d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase;d.ai_on=false;d.meter.value=300;d.effects_enabled=false;d.fx.shake_strength=0;d.cinematic.reduced=true;d.request_main(slot)
			var previous:=0
			for t in range(600):
				d.simulate_tick();d._process(1.0/60)
				if d.hit_log.size()>previous:
					previous=d.hit_log.size();await process_frame;await RenderingServer.frame_post_draw
					root.get_texture().get_image().save_png("res://docs/roster16_contacts/%d_%d_%d.png" % [cid,slot,previous])
			print("RENDER ",cid," slot ",slot," hits ",previous)
	d.queue_free();await process_frame;quit()
