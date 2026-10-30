extends SceneTree
func _initialize() -> void:run.call_deferred()
func run() -> void:
	var d: BattleDemo=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.preview_only=true;d.set_process(false);d.fx.audio_enabled=false
	var samples: Array[int]=[]
	var max_nodes:=0
	var started:=Time.get_ticks_usec()
	for run_index in range(12):
		d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase;d.meter.value=300;d.ai_on=false
		d.request_main(7)
		for i in range(550):
			var begin:=Time.get_ticks_usec();d.simulate_tick();d._process(1.0/60);samples.append(Time.get_ticks_usec()-begin)
			max_nodes=maxi(max_nodes,int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT)))
	samples.sort()
	print("CPU LOGIC+FX: ticks=",samples.size()," total_ms=",(Time.get_ticks_usec()-started)/1000," median_us=",samples[samples.size()/2]," p95_us=",samples[int(samples.size()*.95)]," max_us=",samples[-1]," max_scene_nodes=",max_nodes)
	print("AUDIO CACHE: ",d.fx.audio.cache.size()," synthesized layers; reusable voices=",d.fx.audio.voices.size())
	d.queue_free();await process_frame;quit()
