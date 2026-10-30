extends SceneTree
var d: BattleDemo
var checks := 0
var failures := 0
func ok(v: bool, name_text: String) -> void:
	checks+=1
	if not v:failures+=1
	print("PASS " if v else "FAIL ",name_text)
func ticks(n: int) -> void:
	for i in range(n):d.simulate_tick()
func fresh(left: bool=false) -> void:
	if left:d.mirror_setup()
	else:d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase
	d.meter.value=300;d.ai_on=false
func reach(t: int) -> void:
	for i in range(500):
		if not d.scheduler.busy(0) or d.scheduler.actions[0].tick>=t:return
		d.simulate_tick()
func actor_hits(actor: int) -> Array:
	return d.hit_log.filter(func(h):return h.actor==actor)
func _initialize() -> void:run.call_deferred()
func run() -> void:
	d=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.versus_mode=false;d.preview_only=true;d.fx.audio_enabled=false
	for definition in d.definitions:
		var validation:=PackageValidator.inspect(definition)
		ok(validation.errors.is_empty(),"package schema / "+definition.display_name)
		print("PACKAGE WARNINGS ",validation.warnings)
	for left in [false,true]:
		var ids: Dictionary={}
		for slot in range(8):
			fresh(left);var before:=d.charges
			ok(d.request_main(slot),"accept slot %d side %s" % [slot,left])
			ok(d.charges==before-(1 if slot<5 else 0),"normal action independent of meter move")
			var move: SequenceData=d.scheduler.actions[0].move
			ids[move.sequence_id]=true
			for i in range(600):
				d.simulate_tick()
				if d.scheduler.busy(0):
					ok(d.actors[0].facing*d.actors[0].native_facing*d.actors[0].visual_attack_direction==d.actors[0].facing,"pose direction agrees with intended attack") if i==25 else false
			ok(d.hit_log.size()==move.hit_events.size(),"all authored strikes connect slot %d side %s: %d" % [slot,left,d.hit_log.size()])
			var tokens: Dictionary={}
			for h in d.hit_log:
				tokens[h.token]=true
				ok(h.strike.has_point(h.contact) and h.hurt.has_point(h.contact),"contact belongs to strike and hurt regions")
			ok(tokens.size()==d.hit_log.size(),"one damage per event/target")
			if slot>=5:ok(d.meter.value==300-move.resource_cost,"meter move cannot refund itself")
			if slot==7:ok(not d.cinematic.active and d.phase!=BattleDemo.Phase.Ultimate and d.world.scale==Vector2.ONE,"ultimate cleans cinematic owner")
		ok(ids.size()==8,"five distinct normals + two specials + ultimate")
	# Screen-space directional capture; actual InputMap press/release, not movement.
	for item in [[false,false,false,false,0],[true,false,false,false,1],[false,true,false,false,2],[false,false,true,false,3],[false,false,false,true,4],[true,true,false,false,2],[true,false,true,true,3],[true,true,true,true,0]]:
		ok(BattleCommands.direction_slot(item[0],item[1],item[2],item[3])==item[4],"deterministic direction selector "+str(item))
	fresh();var press:=InputEventKey.new();press.physical_keycode=KEY_J;press.pressed=true
	d._unhandled_key_input(press);var id: int=d.scheduler.actions[0].id
	press.echo=true;d._unhandled_key_input(press);ticks(15)
	ok(d.charges==3 and d.scheduler.actions[0].id==id,"held/echo J never repeatedly spends")
	# Every normal and special: cancel adjacent to each major strike.
	for slot in range(7):
		var move: SequenceData=load(d.move_path(slot))
		for event in move.hit_events:
			for offset in [-1,3]:
				var at: int=int(event.tick)+int(offset)
				if at<move.cancel_open or at>move.cancel_close:continue
				fresh();d.request_main(slot);reach(at)
				var released:=d.projectiles.shots.size()
				var before:=d.hit_log.size();var meter_before:=d.meter.value
				ok(d.request_cancel(),"cancel slot %d at %d" % [slot,at])
				ok(d.meter.value==meter_before-d.rules.cancel_cost,"cancel charges exactly once")
				ok(not d.request_cancel(),"repeated cancel rejected")
				ticks(140)
				ok(d.hit_log.size()<=before+released,"no unexecuted strike/spawn after cancel")
				ok(not d.scheduler.busy(0) and d.actors[0].release_ticks==0,"cancel motion/pose recovered")
	fresh();d.request_main(0);reach(32);d.request_main(1);var c:=d.charges
	d.request_cancel();ok(d.buffer_slot==-1 and d.scheduler.busy(0) and d.scheduler.actions[0].move.sequence_id=="kosmos_barrage" and d.charges==c,"cancel transfers accepted buffer and spends next action")
	reach(10);d.request_cancel();ok(d.cancel_bonus_used==1 and d.charges==3,"extra action limited to one per phase")
	fresh();d.request_main(0);d.request_assist(1);d.request_assist(2);reach(12);d.request_cancel();ticks(140)
	ok(actor_hits(1).size()==3 and actor_hits(2).size()==2,"both multi-hit assists survive main cancel")
	# Grounded and airborne assist repeatability, with sides swapped.
	for left in [false,true]:
		for actor in [1,2]:
			for delay in [-1,40,100]:
				for repeat in range(2):
					fresh(left)
					if delay>=0:d.request_main(2);ticks(delay)
					d.request_assist(actor);ticks(150)
					ok(actor_hits(actor).size()==(3 if actor==1 else 2),"assist %d side %s delay %d repeat %d" % [actor,left,delay,repeat])
	# F4 miss geometry: no gains or contact flashes, ultimate whiff cleans up.
	for slot in range(8):
		d.miss_setup();d.meter.value=300;var cost: int=(load(d.move_path(slot)) as SequenceData).resource_cost
		d.request_main(slot);ticks(240)
		ok(d.hit_log.is_empty() and d.hp==d.rules.target_hp and d.meter.value==300-cost,"F4 slot %d honest miss / no gain" % slot)
		ok(not d.cinematic.active and d.fx.bursts.is_empty(),"miss has no fake impact/cinematic lock")
	for actor in [1,2]:
		d.miss_setup();d.request_assist(actor);ticks(120);ok(d.hit_log.is_empty(),"F4 assist no invisible damage")
	# Reaction unit tests: boundary contact, one bounce, bounded Cross release.
	var motion:=TargetMotion.new();motion.origin_x=640
	motion.apply_event({"horizontal_speed":10,"wall_bounce":true,"launch":200,"hitstun":100},1)
	for i in range(30):motion.advance()
	ok(motion.wall_events.is_empty(),"wall flag without wall contact never bounces")
	motion.reset();motion.origin_x=1100;motion.apply_event({"horizontal_speed":1000,"wall_bounce":true,"launch":300,"hitstun":100},1)
	for i in range(8):motion.advance()
	ok(motion.wall_events.size()==1 and motion.wall_events[0].x==1160 and motion.horizontal_velocity<0,"actual boundary causes rebound")
	motion.apply_event({"horizontal_speed":1000,"wall_bounce":true,"hitstun":100},1)
	for i in range(10):motion.advance()
	ok(motion.wall_events.size()==1,"one wall bounce per combo")
	motion.reset();motion.height=70;motion.velocity=200;motion.horizontal_velocity=30;motion.suspend(12)
	for i in range(8):motion.apply_event({"launch":440,"hitstun":50},1);motion.advance()
	ok(motion.height==70,"Cross suspends target height while impacts continue")
	for i in range(100):motion.advance()
	ok(motion.cross_ticks==0 and motion.height==0 and absf(motion.velocity)<=440,"Cross releases without accumulated extreme impulse")
	fresh();d.request_main(0);d.request_assist(1);ticks(100)
	ok(d.cross_count>0 and d.cross_count<=2 and d.dummy.motion.cross_ticks==0,"real main/assist overlap triggers bounded Cross")
	# Ultimate ownership gates and lethal cleanup.
	fresh();d.request_assist(1);ok(not d.request_main(7) and d.meter.value==300,"ultimate waits for independent assist")
	fresh();ok(d.request_main(7),"ultimate activation");ok(not d.request_main(7) and d.meter.value==0,"ultimate cannot double spend")
	ok(not d.request_assist(1) and not d.request_cancel(),"ultimate locks combat inputs")
	ticks(600);ok(not d.cinematic.active and Engine.time_scale==1 and d.world.scale==Vector2.ONE,"ultimate restores time/camera/input ownership")
	fresh();d.hp=1;d.request_main(7);ticks(680)
	ok(d.phase==BattleDemo.Phase.Victory and not d.cinematic.active and not d.scheduler.busy(0),"lethal ultimate finishes cleanup before victory")
	for slot in [0,1,7]:
		for at in [10,24,90,140]:
			fresh();d.request_main(slot);ticks(at);d.reset_match();ticks(100)
			ok(d.hit_log.is_empty() and d.scheduler.actions.is_empty() and d.projectiles.shots.is_empty() and not d.cinematic.active and d.world.scale==Vector2.ONE and d.fx.numbers.is_empty(),"reset owns all callbacks/effects at slot %d tick %d" % [slot,at])
	fresh();d.request_main(0);d.request_assist(1);ticks(23);d.reset_match();ok(d.dummy.motion.cross_ticks==0 and d.fx.cross_life<0,"reset clears Cross")
	# Individual CPU-hit defenses and full alternating loop remain intact.
	for round_index in [0,1]:
		for tactic in ["none","hold","perfect","dodge","early"]:
			fresh();d.ai_on=true;d.cpu_round=round_index;d._begin_cpu_phase()
			if tactic=="hold":d.defense.block(true)
			var first:=52 if round_index==0 else 70
			while d.scheduler.busy(3):
				var t: int=d.scheduler.actions[3].tick
				if tactic=="perfect" and t==first-2:d.defense.block(true)
				if tactic=="dodge" and t==first-2:d.defense.dodge()
				if tactic=="early" and t==first-12:d.defense.dodge()
				d.simulate_tick()
			var expected: Dictionary={"none":"HIT","hold":"BLOCK","perfect":"PERFECT BLOCK","dodge":"DODGE","early":"CAUGHT IN DODGE RECOVERY"}
			ok(d.cpu_log.size()==2 and d.cpu_log[0].result==expected[tactic],"CPU per-hit defense %d %s" % [round_index,tactic])
			if tactic=="perfect":ok(d.cpu_log[1].result=="BLOCK","perfect block does not cover later strike")
			if tactic=="dodge":ok(d.cpu_log[1].damage>0,"dodge does not protect whole sequence")
			ticks(60);ok(d.phase==BattleDemo.Phase.PlayerAttackPhase,"CPU returns to player phase")
	fresh();d.player_hp=1;d.ai_on=true;d._begin_cpu_phase();ticks(240);ok(d.phase==BattleDemo.Phase.Defeat,"defeat supported")
	fresh();d.swap_role(0,1);d.phase=BattleDemo.Phase.PlayerAttackPhase
	ok(d.request_main(0) and d.request_assist(1),"role swap uses data / authored main accepts")
	ticks(130);ok(actor_hits(1).size()==2,"KOS-MOS assist package works in swapped role")
	var missing: SequenceData=load("res://moves/kosmos_arc.tres").duplicate(true)
	missing.poses=[{"path":"res://missing.png","ticks":78}]
	fresh();d.scheduler.start(0,missing);AttackStaging.prepare(d.scheduler.actions[0],d.actors[0],d.dummy,false);ticks(130)
	ok(d.scheduler.actions.is_empty(),"missing artwork cannot deadlock timeline")
	# End-of-budget meter choices remain usable after every active action resolves.
	d.swap_role(0,0);fresh();d.charges=0;d.assist_used=[true,true];ticks(2)
	ok(d.phase==BattleDemo.Phase.PlayerAttackPhase and d.request_main(7),"ultimate remains selectable with zero normal actions")
	fresh();d.meter.value=59;d.request_main(0);reach(10)
	ok(not d.request_cancel() and d.meter.value==59 and d.scheduler.busy(0),"unaffordable cancel leaves live timeline untouched")
	d.late_setup();ticks(140)
	ok(actor_hits(2).size()==1 and d.contact_log.any(func(h):return h.actor==2 and h.result=="target below strike region"),"F5 late knee contacts but heel misses vertically")
	fresh();d.meter.value=0;d.request_main(0);ticks(130)
	ok(d.meter.value==24,"normal meter gain once per two contact events")
	fresh();d.request_main(0);d.request_assist(1);ticks(22)
	d._override_phase(BattleDemo.Phase.CPUAttackPhase)
	ok(d.dummy.motion.cross_ticks==0 and not d.cinematic.active and not d.scheduler.busy(1),"phase override clears independent ownership")
	d.queue_free();await process_frame
	print("MILESTONE ACCEPTANCE: %d checks / %d failures" % [checks,failures]);quit(1 if failures else 0)
