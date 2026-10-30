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
func _initialize()->void:run.call_deferred()
func run()->void:
 d=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.preview_only=true;d.set_process(false);d.set_physics_process(false);d.fx.audio_enabled=false
 var teams:Dictionary={}
 for i in range(20):
  d.reset_match();teams[str(d.cpu_team)]=true
  ok(d.cpu_team[0]!=d.cpu_team[1] and d.cpu_team[0]!=d.cpu_team[2] and d.cpu_team[1]!=d.cpu_team[2],"unique random CPU slots")
 ok(teams.size()>1,"random teams across rematches")
 for cid in range(d.definitions.size()):
  d.reset_match();d.cpu_team.assign([cid,(cid+1)%d.definitions.size(),(cid+2)%d.definitions.size()])
  for i in range(3):d.cpu_actors[i].configure(d.definitions[d.cpu_team[i]],Vector2(890+i*65,520))
  d.infinite_player_hp=true;d._begin_cpu_phase()
  for t in range(1400):
   ticks(1)
   if d.phase!=BattleDemo.Phase.CPUAttackPhase:break
  ok(d.cpu_log.size()>0,"CPU roster contacts "+str(cid))
  var valid:=true;var seen:Dictionary={}
  for h in d.cpu_log:
   valid=valid and h.strike.intersects(h.hurt) and not seen.has(h.token);seen[h.token]=true
  ok(valid,"honest deduplicated contacts")
  ok(d.phase!=BattleDemo.Phase.CPUAttackPhase,"CPU phase returns")
  d._begin_cpu_phase();ticks(60);d.reset_match()
  ok(d.scheduler.actions.is_empty() and d.projectiles.shots.is_empty(),"CPU reset cleanup")
 for cid in range(6):
  d.reset_match();d.cpu_team.assign([cid,(cid+1)%d.definitions.size(),(cid+2)%d.definitions.size()])
  d.actors[0].home=Vector2(890,520);d.actors[0].sample({})
  for i in range(3):d.cpu_actors[i].configure(d.definitions[d.cpu_team[i]],Vector2(315-i*65,520))
  d.cpu_meter=120;d.infinite_player_hp=true;d._begin_cpu_phase();d.defense.block(true)
  ok(d.cpu_meter<120,"CPU special cost once")
  for t in range(1600):
   ticks(1)
   if d.phase!=BattleDemo.Phase.CPUAttackPhase:break
  ok(d.cpu_log.any(func(h):return "special" in h.sequence),"mirrored CPU special contacts "+str(cid))
  ok(d.cpu_log.any(func(h):return h.result=="BLOCK"),"roster hits respect block")
  ok(d.phase!=BattleDemo.Phase.CPUAttackPhase,"mirrored CPU resolves")
 d.versus_mode=false;d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase;d.ai_on=false;d.meter.value=300;d.request_main(7);ticks(600)
 ok(d.hit_log.size()==9,"particle ultimate nine exposure pulses")
 ok(not d.cinematic.active and not d.weapon.active,"particle ultimate cleanup")
 print("VERSUS: %d checks / %d failures"%[checks,failures]);d.queue_free();await process_frame;quit(1 if failures else 0)
