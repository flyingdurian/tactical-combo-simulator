extends SceneTree
func _initialize() -> void:run.call_deferred()
func run() -> void:
	var d: BattleDemo=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.preview_only=false;d.set_physics_process(false);d.set_process(false);d.fx.audio_enabled=false
	DirAccess.make_dir_recursive_absolute("res://capture4")
	var title:=Label.new();title.position=Vector2(345,37);title.z_index=70;title.add_theme_font_size_override("font_size",13);d.add_child(title)
	var scenes: Array[String]=["1 LIGHT / neutral sequence","2 HEAVY / final heel impact","3 ELECTRICAL / rescue special","4 ENERGY / concentrated volley special","5 FULL DEDICATED ULTIMATE / all nine actual connections","6 RESET DURING CAPTURE -> normal input works","7 DEDICATED ULTIMATE / sides swapped","8 REDUCED / density 0, shake 0, flash 0"]
	var lengths: Array[int]=[110,130,160,160,560,350,560,560]
	var frame:=0
	for scenario in range(scenes.size()):
		if scenario==6:d.mirror_setup()
		else:d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase
		d.ai_on=false;d.meter.value=300;d.infinite_meter=false
		d.cinematic.reduced=scenario==7;d.fx.reduced_flash=scenario==7;d.fx.effect_density=0 if scenario==7 else 1
		d.fx.shake_strength=0 if scenario==7 else .35;d.fx.flash_strength=0 if scenario==7 else .12
		title.text=scenes[scenario]
		var before:=Time.get_ticks_usec()
		for t in range(lengths[scenario]):
			if t==10:d.request_main([0,3,6,5,7,7,7,7][scenario])
			if scenario==5 and t==235:d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase
			if scenario==5 and t==245:d.request_main(0)
			d._physics_process(1.0/60);d._process(1.0/60)
			if t%2==0:
				await process_frame;await RenderingServer.frame_post_draw
				var img:=root.get_texture().get_image();img.save_png("res://capture4/frame_%04d.png" % frame)
				if t in [28,60,90,128,180,240,330,408,470]:img.save_png("res://docs/Impact4_scene_%d_tick_%d.png" % [scenario+1,t])
				frame+=1
		print("CAPTURE ",scenes[scenario]," contacts=",d.hit_log.size()," damage=",d.total_damage," ultimate_summary=",d.cinematic.summary," owner=",d.presentation.owner," target_owner=",d.dummy.motion.owner," elapsed_capture_ms=",(Time.get_ticks_usec()-before)/1000)
	d.queue_free();await process_frame;print("CAPTURE FRAMES ",frame);quit()
