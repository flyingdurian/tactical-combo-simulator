extends SceneTree
func _initialize()->void:run.call_deferred()
func run()->void:
 var d:BattleDemo=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.versus_mode=false;d.preview_only=true;d.set_process(false);d.set_physics_process(false);d.fx.audio_enabled=false
 DirAccess.make_dir_recursive_absolute("res://capture_chest")
 d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase;d.ai_on=false;d.meter.value=300;d.request_main(7)
 for frame in range(300):
  for i in range(2):d.simulate_tick();d._process(1.0/60)
  await process_frame;await RenderingServer.frame_post_draw
  root.get_texture().get_image().save_png("res://capture_chest/%04d.png"%frame)
 print("CHEST CAPTURE: ",d.hit_log.size()," hits, damage ",d.cinematic.summary.y," active=",d.cinematic.active)
 d.queue_free();await process_frame;quit()
