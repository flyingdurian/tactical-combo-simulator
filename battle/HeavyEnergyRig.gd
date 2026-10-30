class_name HeavyEnergyRig
extends Node2D
## Continuous presentation and discrete scheduler-owned exposure pulses.
var attacker: BattleActor
var target: BattleActor
var active:=false
var tick:=0
var density:=1.0
var reduced:=false
var beams:Array[Dictionary]=[]
var beam_tokens:Dictionary={}
var emissions:Array[Dictionary]=[]
var captured:=false
var beam_range:=300.0
var pulse:=0.0
func source()->Vector2:
	return attacker.anchor_world("muzzle",Vector2(148,-104))
func beam_finish()->Vector2:
	var direction:=Vector2(attacker.facing,0)
	if captured:direction=(target.position+Vector2(0,-88-target.elevation)-source()).normalized()
	return source()+direction*beam_range
func emit_beam(event:Dictionary,token:String,is_captured:bool)->Rect2:
	captured=is_captured;beam_range=float(event.get("beam_range",300))
	var start:=source();var finish:=beam_finish();var width:=float(event.get("beam_width",34))
	if not beam_tokens.has(token):
		beam_tokens[token]=true;pulse=1
		emissions.append({"token":token,"from":start,"to":finish,"width":width,"tick":tick})
	return segment_contact(start,finish,width,target.hurt_region())
static func segment_contact(start: Vector2, finish: Vector2, width: float, hurt: Rect2) -> Rect2:
	# Slab clipping against the hurt rectangle expanded by beam half-width.
	var box:=hurt.grow(width*.5)
	var delta:=finish-start
	var enter:=0.0;var leave:=1.0
	for axis in range(2):
		if absf(delta[axis])<.0001:
			if start[axis]<box.position[axis] or start[axis]>box.end[axis]:return Rect2()
		else:
			var a: float=(box.position[axis]-start[axis])/delta[axis]
			var b: float=(box.end[axis]-start[axis])/delta[axis]
			enter=maxf(enter,minf(a,b));leave=minf(leave,maxf(a,b))
			if enter>leave:return Rect2()
	var contact:=start.lerp(finish,clampf((enter+leave)*.5,0,1))
	return Rect2(contact-Vector2.ONE*width*.5,Vector2.ONE*width)
func advance(delta:float)->void:
	pulse=move_toward(pulse,0,delta*5)
	captured=is_instance_valid(target) and target.motion.owner==TargetMotion.Owner.Cinematic
	beams.clear()
	if active and tick>=110 and tick<366:beams.append({"from":source(),"to":beam_finish(),"width":78.0 if tick>=350 else 54.0})
	queue_redraw()
func stop()->void:
	active=false;captured=false;beams.clear();queue_redraw()
func clear_all()->void:
	stop();tick=0;pulse=0;beam_tokens.clear();emissions.clear()
func _draw()->void:
	if active and is_instance_valid(attacker):
		var deploy:=smoothstep(28,76,tick)*(1-smoothstep(382,420,tick))
		var muzzle:=source()
		var opening:=smoothstep(30,95,tick)*(1-smoothstep(366,408,tick))
		for petal in range(6):
			var a:=petal*TAU/6+sin(tick*.02)*.12
			var radial:=Vector2(cos(a),sin(a));var tangent:=Vector2(-radial.y,radial.x)
			var at:=muzzle+radial*(5+opening*8)
			draw_colored_polygon(PackedVector2Array([at+radial*6,at+tangent*4,at-radial*3,at-tangent*4]),Color(.65,.88,1,opening*.8))
		if deploy>0:
			# Body-mounted energy aperture, not a hand-held railgun.
			var charge:=clampf((tick-30)/80.0,0,1) if tick<110 else .6
			draw_circle(muzzle,5+charge*8,Color(.2,.8,1,.7*deploy))
			draw_circle(muzzle,3+charge*3,Color(1,1,.9,deploy))
			for ring in range(2):
				draw_arc(muzzle,12+ring*9+charge*7,tick*.04+ring,tick*.04+ring+PI*1.5,24,Color(.4,.85,1,.65*deploy),2)
			for i in range(clampi(roundi(28*density),0,40)):
				var phase:=fposmod(tick*.026+i*.137,1)
				var angle:=i*2.399
				var offset:=Vector2(cos(angle),sin(angle))*(12+(1-phase)*85)
				draw_line(muzzle+offset,muzzle+offset*.85,Color(.4,.85,1,phase*.7*deploy),2)

	for beam in beams:
		var width:float=beam.width*(1.0+.065*sin(tick*.44))
		var start:Vector2=beam.from;var finish:Vector2=beam.to
		var axis:Vector2=(finish-start).normalized()
		var normal:=Vector2(-axis.y,axis.x)
		for i in range(clampi(roundi(40*density),0,60)):
			var progress:=fposmod(tick*.045+i*.618,1)
			var spread:=sin(i*2.399+tick*.05)*width*.65
			var at:Vector2=start.lerp(finish,progress)+normal*spread
			draw_line(at-axis*(10+12*progress),at,Color(.3,.8,1,.7),2+progress*3)
		draw_line(start,finish,Color(.2,.55,1,.18),width*2)
		var outline:=PackedVector2Array()
		for j in range(17):
			var u:=j/16.0
			outline.append(start.lerp(finish,u)+normal*(width*(.15+.6*u)+sin(j*1.8+tick*.3)*4))
		for j in range(16,-1,-1):
			var u:=j/16.0
			outline.append(start.lerp(finish,u)-normal*(width*(.15+.6*u)+cos(j*1.6+tick*.27)*4))
		draw_colored_polygon(outline,Color(.18,.7,1,.65))
		draw_line(start,finish,Color(.7,.95,1,.95),width*.43)
		draw_line(start,finish,Color(1,1,.93),width*.2)
		var region:=segment_contact(start,finish,width,target.hurt_region())
		if region.has_area():
			var contact:=region.get_center()
			draw_circle(contact,width*.85+pulse*7,Color(.25,.8,1,.22))
			draw_arc(contact,width*.7+pulse*8,0,TAU,24,Color(.75,.95,1,.8),3)
			if density>0:
				for i in range(6):
					var angle:=i*TAU/6+tick*.07;var offset:=Vector2(cos(angle),sin(angle))
					draw_line(contact+offset*width*.4,contact+offset*(width+pulse*12),Color(.6,.9,1,.7),2)
