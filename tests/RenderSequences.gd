extends SceneTree
func _initialize() -> void:run.call_deferred()
func run() -> void:
	var d: BattleDemo=load("res://scenes/BattleDemo.tscn").instantiate();root.add_child(d);d.preview_only=false;d.set_physics_process(false);d.set_process(false);d.fx.audio_enabled=false
	DirAccess.make_dir_recursive_absolute("res://capture3")
	var title:=Label.new();title.position=Vector2(350,245);title.z_index=70;title.add_theme_font_size_override("font_size",18);d.add_child(title)
	var scenes: Array[String]=["1 / FULL NEUTRAL SEQUENCE — two authored thrusts","2 / CANCEL after first hit -> UP launcher (60 meter)","3 / CHAIN + BOTH ASSISTS + CROSS HIT -> DOWN finish","4 / RIGHT drive -> actual WALL BOUNCE -> LEFT volley","5 / SPECIAL 2 -> ULTIMATE [INFINITE METER TRAINING]","6 / DELIBERATE LATE ASSIST — partial whiff / combo drops","7 / SAME STRING — SIDES SWAPPED","8 / COMBO -> CPU BLOCK / DODGE -> YOUR TURN","9 / ULTIMATE CONTACT INSPECTION — NO IMPACT FX"]
	var frame:=0
	for scene_index in range(scenes.size()):
		if scene_index==6:d.mirror_setup()
		else:d.reset_match();d.phase=BattleDemo.Phase.PlayerAttackPhase
		d.effects_enabled=scene_index!=8;d.infinite_meter=scene_index==4;d.meter.value=300 if scene_index in [1,4,8] else 0
		d.ai_on=scene_index==7
		title.text=scenes[scene_index]
		var flags: Dictionary={}
		var length:=380 if scene_index==4 else 300 if scene_index==8 else 580 if scene_index==7 else 210
		for tick in range(length):
			if tick==10:
				d.request_main(4 if scene_index==3 else 6 if scene_index==4 else 2 if scene_index==5 else 7 if scene_index==8 else 0)
				if scene_index in [2,6,7]:d.request_assist(1)
			if tick==22 and scene_index in [2,6,7]:d.request_assist(2)
			if scene_index==5 and tick==90:d.request_assist(2)
			if d.scheduler.busy(0):
				var action: Dictionary=d.scheduler.actions[0]
				if scene_index==1 and not flags.has("cancel") and action.tick>=24:
					d.request_cancel();d.request_main(2);flags.cancel=true
				if scene_index in [2,6,7] and action.move.sequence_id=="kosmos_arc" and action.tick>=35 and not flags.has("sustain"):
					d.request_main(1);flags.sustain=true
				if scene_index in [2,6,7] and action.move.sequence_id=="kosmos_barrage" and action.tick>=48 and not flags.has("finish"):
					d.request_main(3);flags.finish=true
			if scene_index==3 and not d.dummy.motion.wall_events.is_empty() and not flags.has("wall"):
				d.request_main(1);flags.wall=true
			if scene_index==4 and tick>30 and not d.scheduler.busy(0) and not flags.has("ult"):
				flags.ult=d.request_main(7)
			if d.scheduler.busy(3):
				var ct:int=d.scheduler.actions[3].tick
				if ct==50 and not flags.has("block"):d.defense.block(true);flags.block=true
				if ct==60:d.defense.block(false)
				if ct==74 and not flags.has("dodge"):d.defense.dodge();flags.dodge=true
			d._physics_process(1.0/60)
			d._process(1.0/60)
			if tick%2==0:
				await process_frame;await RenderingServer.frame_post_draw
				var img:=root.get_texture().get_image()
				img.save_png("res://capture3/frame_%04d.png" % frame)
				if tick in [34,58,90,120,152,180,210,250,300,440,530]:img.save_png("res://docs/Sequence_%d_tick_%d.png" % [scene_index+1,tick])
				frame+=1
		print("CAPTURED ",scenes[scene_index]," / hits=",d.hit_log.size()," hits_log=",d.hit_log," wall=",d.dummy.motion.wall_events," cpu=",d.cpu_log)
	d.queue_free();await process_frame;print("CAPTURE FRAMES ",frame);quit()
