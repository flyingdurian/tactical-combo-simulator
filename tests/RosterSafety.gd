extends SceneTree
var d:BattleDemo
var checks:=0
var failures:=0
func ok(v:bool,s:String)->void:
 checks+=1
 if not v:failures+=1
 print("PASS " if v else "FAIL ",s)
func ticks(n:int)->void:
 for i in range(n):d.simulate_tick();d._process(1.0/60)
func fresh(cid:int)->void:
 d.roles.assign([cid,(cid+1)%6,(cid+2)%6]);d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase;d.ai_on=false;d.meter.value=300;d.infinite_hp=true
func _initialize()->void:run.call_deferred()
func run()->void:
 d=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.versus_mode=false;d.preview_only=true;d.set_process(false);d.set_physics_process(false);d.fx.audio_enabled=false
 for cid in range(d.definitions.size()):
  var report:=PackageValidator.inspect(d.definitions[cid])
  ok(report.errors.is_empty(),"package "+str(cid)+str(report.errors))
  for slot in range(7):
   fresh(cid)
   if d.move_path(slot).is_empty():continue
   var move:SequenceData=load(d.move_path(slot))
   for event in move.hit_events:
    for offset in [-1,3]:
     var at:int=int(event.tick)+int(offset)
     if at<move.cancel_open or at>move.cancel_close:continue
     fresh(cid);d.request_main(slot);ticks(at)
     var before:=d.hit_log.size();var shots:=d.projectiles.shots.size();var meter:=d.meter.value
     ok(d.request_cancel(),"cancel %d/%d/%d"%[cid,slot,at])
     ok(d.meter.value==meter-d.rules.cancel_cost,"single cancel cost")
     ticks(move.duration_ticks+80)
     ok(d.hit_log.size()<=before+shots and not d.scheduler.busy(0),"no ghost strikes")
  fresh(cid)
  if d.move_path(7).is_empty():continue
  var ult:SequenceData=load(d.move_path(7))
  for at in [20,80,150,250,350]:
   fresh(cid);d.request_main(7);ticks(mini(at,ult.duration_ticks-1));d.reset_match();ticks(600)
   ok(d.hit_log.is_empty() and not d.cinematic.active and not d.weapon.active and d.presentation.owner=="battle","ultimate reset %d/%d"%[cid,at])
 fresh(0);d.request_main(0);var roles:=d.roles.duplicate();d.stage_role(0,4)
 ok(d.roles==roles and d.scheduler.busy(0),"selection pending during action")
 d.apply_team();ok(d.roles[0]==4 and d.scheduler.actions.is_empty() and d.hit_log.is_empty(),"team launch clears old actions")
 print("ROSTER SAFETY: %d checks / %d failures"%[checks,failures]);d.queue_free();await process_frame;quit(1 if failures else 0)
