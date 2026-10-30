extends SceneTree
func _initialize() -> void:run.call_deferred()
func run() -> void:
	var d: BattleDemo=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.preview_only=true;d.fx.audio_enabled=false
	for actor in [1,2]:
		for delay in [0,24,40,50,60,70,80,90,100]:
			d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase;d.request_main(2)
			for i in range(delay):d.simulate_tick()
			d.request_assist(actor)
			for i in range(130):d.simulate_tick()
			print("ASSIST ",actor," DELAY ",delay," HITS ",d.hit_log.filter(func(h):return h.actor==actor).size())
			if actor==1 and delay==40:print(d.contact_log.filter(func(h):return h.actor==actor))
	d.queue_free();await process_frame;quit()
