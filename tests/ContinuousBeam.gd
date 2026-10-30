extends SceneTree
var failures:=0
func check(v:bool,label:String)->void:
	print("PASS " if v else "FAIL ",label)
	if not v:failures+=1
func _initialize()->void:run.call_deferred()
func run()->void:
	var d:BattleDemo=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.versus_mode=false;d.preview_only=true;d.set_process(false);d.set_physics_process(false);d.fx.audio_enabled=false
	for mirror in [false,true]:
		if mirror:d.mirror_setup()
		else:d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase
		d.meter.value=300;d.ai_on=false;d.request_main(7)
		var continuous:=true;var aligned:=true;var observed:=0
		for t in range(550):
			d.simulate_tick();d._process(1.0/60)
			if d.weapon.active and d.weapon.tick>=110 and d.weapon.tick<366:
				observed+=1;continuous=continuous and d.weapon.beams.size()==1
				aligned=aligned and d.weapon.source().distance_to(d.actors[0].anchor_world("muzzle"))<.01
		check(continuous and observed>200,"uninterrupted beam / side "+str(mirror))
		check(aligned,"mirrored muzzle anchor")
		check(d.hit_log.size()==9 and d.cinematic.summary.y==165,"nine pulses / exact damage")
		check(d.weapon.beams.is_empty() and d.presentation.owner=="battle","release cleanup")
	d.queue_free();await process_frame;print("CONTINUOUS BEAM: 8 checks / ",failures," failures");quit(failures)
