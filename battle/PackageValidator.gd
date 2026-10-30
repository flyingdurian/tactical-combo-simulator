class_name PackageValidator
extends RefCounted
## Individual PNG poses replace sprite-frame indices in this pipeline.
static func inspect(data:CharacterDefinition)->Dictionary:
	var errors:Array[String]=[];var warnings:Array[String]=[]
	if data.character_id.is_empty():errors.append("Missing character ID")
	if data.main_sequences.size()!=5:errors.append("Five normal slots required")
	if data.special_sequences.size()!=2:errors.append("Two special slots required")
	if data.native_facing not in [-1,1]:errors.append("Invalid native facing")
	if data.sprite_scale<=0:errors.append("Invalid battle scale")
	if data.hurtbox.size.x<=0 or data.hurtbox.size.y<=0:errors.append("Invalid hurtbox")
	var paths:Array[String]=[];paths.append_array(data.main_sequences);paths.append_array(data.special_sequences);paths.append_array(data.assist_variants);paths.append(data.ultimate_sequence)
	var normal_paths:Dictionary={}
	for path in data.main_sequences:
		if not path.is_empty() and normal_paths.has(path):errors.append("Duplicate normal slot: "+path)
		if not path.is_empty():normal_paths[path]=true
	for path in paths:
		if path.is_empty():warnings.append("Explicit unavailable slot");continue
		if not ResourceLoader.exists(path):errors.append("Missing move: "+path);continue
		var move=load(path)
		if not move is SequenceData:errors.append("Invalid move resource: "+path);continue
		if move.character!=data.character_id:errors.append("Wrong character identity: "+path)
		if move.duration_ticks<=0:errors.append("Invalid duration: "+path)
		var ids:Dictionary={};var pose_ticks:=0
		for pose in move.poses:
			pose_ticks+=int(pose.get("ticks",0))
			if int(pose.get("ticks",0))<=0:errors.append("Nonpositive pose duration: "+path)
			if not ResourceLoader.exists(str(pose.get("path",""))):warnings.append("Missing artwork: "+str(pose.get("path","")))
			if pose.get("anchor",[]).size()!=2:errors.append("Missing pivot: "+path)
			if int(pose.get("native_facing",data.native_facing)) not in [-1,1]:errors.append("Invalid pose facing: "+path)
			if pose.has("frame_index"):errors.append("PNG pose pipeline does not accept frame_index: "+path)
		for event in move.hit_events:
			var id:=str(event.get("id",""))
			if id.is_empty() or ids.has(id):errors.append("Missing/duplicate event ID: "+path)
			ids[id]=true
			var first:=int(event.get("tick",-1));var last:=int(event.get("end_tick",first))
			if first<0 or last<first or last>=move.duration_ticks:errors.append("Invalid event interval: "+path)
			if event.get("kind","melee")=="melee" and event.get("region",[]).size()!=4:errors.append("Missing contact geometry: "+path)
			if event.has("origin_anchor"):
				var at:=0;var found:=false
				for pose in move.poses:
					if first>=at and first<at+int(pose.ticks):found=pose.get("anchors",{}).has(str(event.origin_anchor)) or data.anchors.has(str(event.origin_anchor))
					at+=int(pose.ticks)
				if not found:errors.append("Missing muzzle anchor: "+path)
		if move.hit_events.size()<2:errors.append("Sequence requires multiple events: "+path)
		if pose_ticks!=move.duration_ticks:warnings.append("Safe final-pose hold: "+path)
		if move.category=="ultimate" and not move.cinematic_spec.is_empty():
			var release:=int(move.cinematic_spec.get("release_tick",-1))
			if release<=int(move.cinematic_spec.get("miss_gate",-1)) or release>=move.duration_ticks:errors.append("Invalid cinematic cleanup interval: "+path)
			for event in move.hit_events:
				if int(event.get("end_tick",event.tick))>=release:errors.append("Damage after release: "+path)
	if data.sound_profile==null:warnings.append("No voice profile / explicit silence")
	return {"errors":errors,"warnings":warnings}
