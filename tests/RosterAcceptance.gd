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
func fresh(cid:int,mirrored:bool=false)->void:
	d.roles.assign([cid,1 if cid!=1 else 0,2 if cid!=2 else 0])
	if mirrored:d.mirror_setup()
	else:d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase
	d.ai_on=false;d.meter.value=300;d.infinite_hp=true
func _initialize()->void:run.call_deferred()
func run()->void:
	d=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.versus_mode=false;d.preview_only=true;d.set_process(false);d.set_physics_process(false);d.fx.audio_enabled=false
	ok(d.definitions.size()==16,"sixteen registered packages load")
	for cid in range(d.definitions.size()):
		for mirror in [false,true]:
			for slot in range(8):
				fresh(cid,mirror)
				if d.move_path(slot).is_empty():continue
				var move:SequenceData=load(d.move_path(slot))
				ok(d.request_main(slot),"start %s side=%s" % [move.sequence_id,mirror])
				ok(d.meter.value==300-move.resource_cost,"single entry cost "+move.sequence_id)
				ticks(move.duration_ticks+180)
				ok(d.hit_log.size()==move.hit_events.size(),"grounded contacts %s %d/%d" % [move.sequence_id,d.hit_log.size(),move.hit_events.size()])
				var seen:Dictionary={};var total:=0;var unique:=true;var contact:=true
				for h in d.hit_log:
					unique=unique and not seen.has(h.token);seen[h.token]=true;total+=int(h.damage)
					contact=contact and h.strike.has_point(h.contact) and h.hurt.has_point(h.contact)
				ok(unique and contact,"dedup and intersected contact "+move.sequence_id)
				ok(d.scheduler.actions.is_empty() and d.projectiles.shots.is_empty() and not d.cinematic.active and d.dummy.motion.owner==TargetMotion.Owner.Ordinary,"resolved owners "+move.sequence_id)
				if slot==7:ok(d.cinematic.summary==Vector2i(d.hit_log.size(),total),"ultimate actual summary "+move.sequence_id)
				fresh(cid,mirror);d.dummy.motion.height=55;d.dummy.motion.velocity=70;d.request_main(slot);ticks(move.duration_ticks+180)
				# Low finishers may genuinely miss after the target rises out of their region.
				ok(d.hit_log.size()>=1 or slot==3,"airborne opportunity "+move.sequence_id)
				ok(d.dummy.motion.owner==TargetMotion.Owner.Ordinary and not d.cinematic.active,"airborne cleanup "+move.sequence_id)
				fresh(cid,mirror);d.request_main(slot);ticks(24);d.reset_match();ticks(move.duration_ticks+90)
				ok(d.hit_log.is_empty() and d.scheduler.actions.is_empty() and d.projectiles.shots.is_empty() and not d.weapon.active,"active reset "+move.sequence_id)
	print("ROSTER ACCEPTANCE: %d checks / %d failures" % [checks,failures]);d.queue_free();await process_frame;quit(1 if failures else 0)
