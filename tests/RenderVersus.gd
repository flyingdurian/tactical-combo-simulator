extends SceneTree
func _initialize()->void:run.call_deferred()
func run()->void:
 var d:BattleDemo=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.preview_only=true;d.set_process(false);d.set_physics_process(false);d.fx.audio_enabled=false
 DirAccess.make_dir_recursive_absolute("res://docs/versus6_captures")
 d.versus_mode=false;d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase;d.ai_on=false;d.meter.value=300;d.request_main(7)
 for t in range(600):
  d.simulate_tick();d._process(1.0/60)
  if t in [85,145,330,430,570]:
   await process_frame;await RenderingServer.frame_post_draw
   root.get_texture().get_image().save_png("res://docs/versus6_captures/particle_%d.png"%t)
 d.versus_mode=true;d.ai_on=true;d.reset_match();d.infinite_player_hp=true;d._begin_cpu_phase()
 for t in range(250):
  d.simulate_tick();d._process(1.0/60)
  if t in [70,110,160]:
   await process_frame;await RenderingServer.frame_post_draw
   root.get_texture().get_image().save_png("res://docs/versus6_captures/cpu_%d.png"%t)
 d.queue_free();await process_frame;quit()
