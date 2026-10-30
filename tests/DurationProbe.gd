extends SceneTree
func _initialize() -> void:run.call_deferred()
func run() -> void:
	var d: BattleDemo=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.set_physics_process(false);d.set_process(false);d.fx.audio_enabled=false
	for shortened in [false,true]:
		d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase;d.meter.value=300;d.cinematic.shortened=shortened;d.request_main(7)
		var ticks:=0
		while d.cinematic.active and ticks<900:d._physics_process(1.0/60);d._process(1.0/60);ticks+=1
		print("ULTIMATE DURATION short=",shortened," presentation_ticks=",ticks," seconds=",ticks/60.0," hits=",d.hit_log.size()," damage=",d.total_damage)
	d.queue_free();await process_frame;quit()
