extends SceneTree
var d:BattleDemo
var checks:=0
var failures:=0
func ok(v:bool,label:String)->void:
	checks+=1
	if not v:failures+=1
	print("PASS " if v else "FAIL ",label)
func ticks(n:int)->void:
	for i in range(n):d.simulate_tick();d._process(1.0/60)
func fresh(cid:int,mirror:bool=false)->void:
	d.roles.assign([1 if cid==0 else 0,cid,2 if cid!=2 else 3]);d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase
	if mirror:d.mirror_setup()
	d.ai_on=false;d.meter.value=300;d.infinite_hp=true
func _initialize()->void:run.call_deferred()
func run()->void:
	d=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.versus_mode=false;d.preview_only=true;d.set_process(false);d.set_physics_process(false);d.fx.audio_enabled=false
	for cid in range(d.definitions.size()):
		var move:SequenceData=load(d.definitions[cid].assist_sequence)
		for mirror in [false,true]:
			for repeat in range(3):
				fresh(cid,mirror);d.request_assist(1);ticks(180)
				ok(d.hit_log.size()==move.hit_events.size(),"repeat grounded %s side=%s %d/%d" % [move.sequence_id,mirror,d.hit_log.size(),move.hit_events.size()])
			fresh(cid,mirror);d.dummy.motion.height=55;d.dummy.motion.velocity=140;d.request_assist(1);ticks(180)
			ok(d.hit_log.size()>0,"juggle opportunity "+move.sequence_id)
			fresh(cid,mirror);d.dummy.motion.height=180;d.dummy.motion.velocity=-650;d.request_assist(1);ticks(180)
			if cid>=6 and (move.hit_events[0].get("kind","")=="projectile" or not move.staging.get("segments",[]).is_empty()):
				ok(d.hit_log.size()<=move.hit_events.size() and d.hit_log.all(func(h):return h.strike.intersects(h.hurt)),"late ground-cover hits remain bounded and real "+move.sequence_id)
				print("OBSERVED late cover ",move.sequence_id,": ",d.hit_log.size())
			else:ok(d.hit_log.is_empty(),"late falling target escapes committed height "+move.sequence_id)
			ok(d.scheduler.actions.is_empty() and d.projectiles.shots.is_empty() and not d.actors[1].visible,"exit cleanup "+move.sequence_id)
			fresh(cid,mirror);d.request_assist(1);ticks(10);d.reset_match();ticks(180)
			ok(d.hit_log.is_empty() and d.scheduler.actions.is_empty(),"assist reset "+move.sequence_id)
	print("ASSIST ROSTER: %d checks / %d failures" % [checks,failures]);d.queue_free();await process_frame;quit(1 if failures else 0)
