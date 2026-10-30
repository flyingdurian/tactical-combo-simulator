extends SceneTree
var d: BattleDemo
var checks:=0
var failures:=0
var max_bursts:=0
var max_arcs:=0
var max_labels:=0
var max_beams:=0
func ok(v: bool, label: String) -> void:
	checks+=1
	if not v:failures+=1
	print("PASS " if v else "FAIL ",label)
func tick(n: int) -> void:
	for i in range(n):
		d.simulate_tick();d._process(1.0/60)
		max_bursts=maxi(max_bursts,d.fx.bursts.size());max_arcs=maxi(max_arcs,d.fx.electrical.discharges.size());max_labels=maxi(max_labels,d.fx.numbers.size());max_beams=maxi(max_beams,d.weapon.beams.size())
func fresh(left: bool=false) -> void:
	if left:d.mirror_setup()
	else:d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase
	d.meter.value=300;d.ai_on=false
func reach(t: int) -> void:
	for i in range(900):
		if not d.scheduler.busy(0) or d.scheduler.actions[0].tick>=t:return
		tick(1)
func _initialize() -> void:run.call_deferred()
func run() -> void:
	d=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.preview_only=true;d.set_process(false);d.fx.audio_enabled=false
	for name in ["light","heavy","ballistic","energy","electrical","launcher","wall","finisher","ultimate"]:
		var profile: ImpactProfile=load("res://impacts/%s.tres" % name)
		ok(profile!=null and profile.spark_count<=18 and profile.electrical_branches<=6,"bounded profile "+name)
	var light: ImpactProfile=load("res://impacts/light.tres");var heavy: ImpactProfile=load("res://impacts/heavy.tres")
	ok(heavy.radius>light.radius and heavy.hitstop>light.hitstop and heavy.number_scale>light.number_scale,"authored heavy contrast")
	for left in [false,true]:
		fresh(left);ok(d.request_main(7),"ultimate starts / side "+str(left))
		ok(not d.request_main(7) and d.meter.value==0,"cost once / duplicate input rejected")
		ok(not d.presentation.claim("ordinary",1),"lower priority cannot steal camera")
		reach(90);ok(d.dummy.motion.owner!=TargetMotion.Owner.Cinematic and d.hit_log.is_empty(),"charge has no invisible damage or premature capture")
		reach(111);ok(d.dummy.motion.owner==TargetMotion.Owner.Cinematic and d.hit_log.size()==1,"capture requires real initial beam connection")
		var captured_x:=d.dummy.motion.displacement
		reach(220);ok(d.dummy.motion.owner==TargetMotion.Owner.Cinematic and d.dummy.motion.displacement==captured_x and is_equal_approx(d.dummy.motion.height,70),"capture owns motion; gravity and horizontal drift suspended")
		reach(365);ok(d.cinematic.hits==9 and d.weapon.emissions.size()==9,"nine authored beam events / nine actual contacts")
		var sum_damage:=0
		for h in d.hit_log:
			sum_damage+=int(h.damage)
			ok(h.strike.has_point(h.contact) and h.hurt.has_point(h.contact),"impact belongs to clipped visible beam/hurt region")
		ok(sum_damage==d.cinematic.damage and d.hp==d.rules.target_hp-sum_damage,"ultimate summary exactly matches actual damage")
		tick(180)
		ok(not d.cinematic.active and d.presentation.owner=="battle" and d.dummy.motion.owner==TargetMotion.Owner.Ordinary,"completion releases all owners")
		ok(d.world.scale.distance_to(Vector2.ONE)<.001 and d.world.position.length()<.1 and Engine.time_scale==1,"smooth camera return / global time unchanged")
		ok(d.weapon.beams.is_empty() and d.fx.electrical.discharges.is_empty(),"weapon/electric residue terminates")
	# Each stage can reset without delayed damage, audio, beam or capture ownership.
	for at in [5,45,111,180,330,361,392]:
		fresh();d.request_main(7);reach(at);d.reset_match();tick(100)
		ok(d.scheduler.actions.is_empty() and d.hit_log.is_empty() and d.weapon.beams.is_empty() and not d.weapon.active,"reset action/weapon stage %d" % at)
		ok(d.dummy.motion.owner==TargetMotion.Owner.Ordinary and d.presentation.owner=="battle" and d.fx.electrical.discharges.is_empty() and d.fx.audio.voices.all(func(v):return not v.playing),"reset owner/audio stage %d" % at)
	fresh();d.hp=1;d.request_main(7);tick(650)
	ok(d.phase==BattleDemo.Phase.Victory and d.cinematic.summary==Vector2i(1,1),"lethal opener latches defeat and reports actual one-point damage")
	ok(d.weapon.emissions.size()==9 and not d.cinematic.active and d.dummy.motion.owner==TargetMotion.Owner.Ordinary,"lethal opener still completes weapon aftermath and cleanup")
	d.miss_setup();d.meter.value=300;d.request_main(7);tick(190)
	ok(d.hit_log.is_empty() and d.fx.contact_effects.is_empty() and d.meter.value==0,"missed opening beam has no contact effects/damage/refund")
	ok(not d.cinematic.active and d.weapon.emissions.size()==1 and d.dummy.motion.owner!=TargetMotion.Owner.Cinematic,"whiff path stops future barrage and capture")
	# Reduced mode does not change hit geometry or damage.
	fresh();d.fx.effect_density=0;d.fx.shake_strength=0;d.fx.flash_strength=0;d.fx.reduced_flash=true;d.cinematic.reduced=true;d.request_main(7);tick(600)
	ok(d.hit_log.size()==9 and d.world.position==Vector2.ZERO and d.world.scale==Vector2.ONE,"zero shake/flash/density retains nine real contacts")
	fresh();d.cinematic.shortened=true;d.preview_only=false;d.set_physics_process(false);d.request_main(7)
	var real_ticks:=0
	while d.cinematic.active and real_ticks<700:
		d._physics_process(1.0/60);d._process(1.0/60);real_ticks+=1
	ok(real_ticks<320 and d.hit_log.size()==9,"shortened presentation preserves all events at faster tempo")
	d.cinematic.shortened=false;d.preview_only=true;d.fx.effect_density=1;d.cinematic.reduced=false
	# Target motion precedence and finite status budgets.
	var motion:=TargetMotion.new();motion.height=40;motion.velocity=180;motion.suspend(12)
	motion.begin_capture(7,4);ok(motion.owner==TargetMotion.Owner.Cinematic and motion.cross_ticks==0,"capture atomically supersedes Cross")
	motion.suspend(99);ok(motion.cross_ticks==0,"Cross cannot steal capture owner")
	motion.end_capture(8);ok(motion.owner==TargetMotion.Owner.Cinematic,"wrong owner cannot release capture")
	for i in range(5):motion.advance()
	ok(motion.owner==TargetMotion.Owner.Ordinary,"capture watchdog releases abandoned state")
	motion.reset()
	for i in range(36):motion.apply_event({"reaction_profile":"res://reactions/electrical_stun.tres","hitstun":10,"launch":0},1);motion.advance()
	ok(motion.electrical_ticks==0 and motion.electrical_uses==1,"electrical status cannot refresh indefinitely")
	motion.reset()
	for i in range(40):motion.apply_event({"launch":440,"hitstun":10000},1)
	ok(motion.launch_count<=motion.maximum_launches and motion.stun_ticks<=90,"launch and per-hit stun limits")
	motion.reset();motion.height=50
	for i in range(10):
		motion.suspend(12)
		for k in range(12):motion.advance()
	ok(motion.suspension_used<=36,"bounded cumulative Cross suspension")
	# Arc anchoring stores target-local endpoints, not stale screen positions.
	fresh();d.request_main(6);reach(51)
	ok(not d.fx.electrical.discharges.is_empty() and d.fx.electrical.discharges[0].target==d.dummy,"electric arcs retain target anchor")
	tick(100);ok(d.fx.electrical.discharges.is_empty() and d.dummy.motion.electrical_ticks==0,"electrical visuals/status end separately")
	ok(max_bursts<=24 and max_arcs<=8 and max_labels<=7 and max_beams<=8,"observed effect budgets")
	print("OBSERVED MAXIMA bursts=",max_bursts," arcs=",max_arcs," labels=",max_labels," beams=",max_beams)
	d.queue_free();await process_frame
	print("IMPACT ACCEPTANCE: %d checks / %d failures" % [checks,failures]);quit(1 if failures else 0)
