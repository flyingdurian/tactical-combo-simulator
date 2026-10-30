extends SceneTree
var d: BattleDemo
var failures := 0
var checks := 0
func ok(v: bool, name_text: String) -> void:
	checks+=1
	if not v: failures+=1
	print("PASS " if v else "FAIL ",name_text)
func ticks(n: int) -> void:
	for i in range(n):d.simulate_tick()
func fresh() -> void:
	d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase;d.meter.value=300
func reach(t: int) -> void:
	for i in range(350):
		if not d.scheduler.busy(0) or d.scheduler.actions[0].tick>=t:return
		d.simulate_tick()
func _initialize() -> void:run.call_deferred()
func run() -> void:
	d=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.preview_only=true;d.fx.audio_enabled=false
	ok(BattleCommands.direction_slot(true,true,false,false)==2,"diagonal vertical priority")
	ok(BattleCommands.direction_slot(true,false,false,true)==0,"opposing directions neutral")
	fresh();d.request_main(0);ticks(130)
	ok(d.hit_log.size()==2,"neutral complete two-hit sequence")
	fresh();d.request_main(0);reach(32)
	ok(d.request_main(1) and d.buffer_slot==1,"bounded buffered directional selection")
	ok(not d.request_main(0),"queue never overwritten")
	ticks(140);ok(d.charges==2 and d.hit_log.any(func(h):return h.sequence=="kosmos_barrage"),"normal chain consumes exactly two actions")
	for t in [8,17,22,35,40]:
		fresh();d.request_main(0);reach(t)
		var id: int=d.scheduler.actions[0].id
		var before := d.hit_log.size()
		var cost_before := d.meter.value
		ok(d.request_cancel(),"cancel at %d" % t)
		ok(d.meter.value==cost_before-60 and d.charges==4,"single cost and bounded bonus")
		ok(not d.request_cancel(),"duplicate cancel rejected")
		ticks(110);ok(d.hit_log.size()==before and not d.scheduler.busy(0),"no ghost damage or frozen action %d" % id)
	fresh();d.request_main(1);reach(18)
	ok(not d.projectiles.shots.is_empty(),"arrow visibly released before cancel")
	d.request_cancel();ticks(100)
	ok(d.hit_log.size()==1,"released arrow persists; future arrows cancelled")
	fresh();d.request_main(0);d.request_assist(1);reach(12);d.request_cancel();ticks(100)
	ok(d.hit_log.filter(func(h):return h.actor==1).size()==3,"assist independent through main cancel")
	fresh();d.request_main(0);reach(12);d.request_cancel();d.reset_match();ticks(100)
	ok(d.scheduler.actions.is_empty() and d.hit_log.is_empty() and d.cancel_slow_left==0,"reset clears cancel timeline and slowdown")
	d.queue_free();await process_frame
	print("FOUNDATION: %d checks / %d failures" % [checks,failures]);quit(1 if failures else 0)
