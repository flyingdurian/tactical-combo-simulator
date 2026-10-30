class_name TargetMotion
extends RefCounted
## Sole owner of target reactions. Ground, height, Cross suspension and wall contact
## are simulation state, never inferred from sprite animation or screen overlap.
enum Owner { Ordinary, Cross, Cinematic }
var owner: Owner = Owner.Ordinary
var capture_id: int = -1
var capture_left: int = 0
var capture_saved := Vector2.ZERO
var captured_x: float = 0
var captured_height: float = 0
var capture_goal_height: float = 70
var capture_age: int = 0
var recoil_left: int = 0
var recoil_duration: int = 1
var recoil_amount: float = 0
var recoil_direction: int = 1
var recoil_tilt: float = 0
var recoil_squash: float = 0
var electrical_ticks: int = 0
var electrical_cooldown: int = 0
var electrical_uses: int = 0
var maximum_electrical_per_combo: int = 1
var launch_count: int = 0
var maximum_launches: int = 6
var stun_budget: int = 500
var maximum_stun_budget: int = 500
var suspension_used: int = 0
var maximum_suspension: int = 36
var height: float = 0
var velocity: float = 0
var displacement: float = 0
var horizontal_velocity: float = 0
var max_displacement: float = 90 # Legacy preview field; real stage boundaries below.
var origin_x: float = 890
var wall_left: float = 120
var wall_right: float = 1160
var stun_ticks: int = 0
var cross_ticks: int = 0
var gravity: float = 850
var maximum_height: float = 200
var juggle_hits: int = 0
var juggle_limit: int = 24
var knockdown: bool = false
var recovery_ticks: int = 0
var wall_bounces: int = 0
var maximum_wall_bounces: int = 1
var bounce_armed: bool = false
var carry_ticks: int = 0
var wall_events: Array[Dictionary] = []
var cross_saved := Vector2.ZERO
var cross_pending := Vector2.ZERO
var cross_has_impulse: bool = false
var cross_releases: int = 0
func begin_capture(id: int, duration: int) -> bool:
	if owner==Owner.Cinematic:return capture_id==id
	if cross_ticks>0:release_cross()
	owner=Owner.Cinematic;capture_id=id;capture_left=clampi(duration,1,420)
	capture_saved=Vector2(horizontal_velocity,velocity)
	captured_x=displacement;captured_height=height;capture_age=0
	cross_ticks=0;knockdown=false;recovery_ticks=0;bounce_armed=false;carry_ticks=0
	return true
func end_capture(id: int, finishing: bool=false) -> void:
	if owner!=Owner.Cinematic or capture_id!=id:return
	owner=Owner.Ordinary;capture_id=-1;capture_left=0
	if finishing:
		horizontal_velocity=0;velocity=-450;knockdown=true;stun_ticks=30
		if height==0:velocity=0;recovery_ticks=40
	else:
		horizontal_velocity=clampf(capture_saved.x,-300,300);velocity=clampf(capture_saved.y,-250,250)
		stun_ticks=mini(stun_ticks,30)
func recoil_x() -> float:
	return recoil_direction*recoil_amount*float(recoil_left)/maxi(1,recoil_duration)
func recoil_weight() -> float:
	return float(recoil_left)/maxi(1,recoil_duration)
func hit(launch: float, stun: int) -> void:
	apply_event({"launch":launch,"hitstun":stun},1)
func suspend(ticks: int) -> void:
	if owner==Owner.Cinematic or cross_ticks > 0 or knockdown or suspension_used>=maximum_suspension: return
	cross_ticks = mini(maxi(1,ticks),maximum_suspension-suspension_used)
	suspension_used+=cross_ticks
	owner=Owner.Cross
	cross_saved = Vector2(horizontal_velocity,velocity)
	cross_pending = cross_saved
	cross_has_impulse = false
func release_cross() -> void:
	# Latest resolved reaction wins, bounded; do not sum impulses during suspension.
	var released := cross_pending if cross_has_impulse else cross_saved
	horizontal_velocity = clampf(released.x,-1000,1000)
	velocity = clampf(released.y,-450,440)
	cross_ticks = 0
	owner=Owner.Ordinary
	cross_releases += 1
func apply_event(event: Dictionary, direction: int) -> void:
	var path:=str(event.get("reaction_profile","res://reactions/light_stagger.tres"))
	var profile: ReactionProfile=load(path)
	recoil_amount=profile.recoil;recoil_duration=profile.recoil_ticks;recoil_left=recoil_duration
	recoil_direction=direction;recoil_tilt=profile.tilt;recoil_squash=profile.squash
	if profile.electrical_ticks>0 and electrical_cooldown==0 and electrical_uses<maximum_electrical_per_combo:
		electrical_ticks=mini(24,profile.electrical_ticks);electrical_cooldown=180;electrical_uses+=1
	if owner==Owner.Cinematic:return
	juggle_hits += 1
	var addition:=mini(maxi(0,mini(90,int(event.get("hitstun",30)))-stun_ticks),stun_budget)
	stun_ticks+=addition;stun_budget-=addition
	var suspended := cross_ticks > 0
	if suspended:
		horizontal_velocity = cross_saved.x
		velocity = cross_saved.y
	var scaling := maxf(.35,1.0-maxi(0,juggle_hits-6)*.055)
	var launch := float(event.get("launch",0))*scaling
	if float(event.get("launch",0))>200:
		if launch_count>=maximum_launches:launch=0
		else:launch_count+=1
	match str(event.get("reaction","launch")):
		"ground":
			if height > 0: velocity = clampf(velocity+70,-100,160)
		"finish":
			knockdown = true;velocity = -450
			if height == 0: recovery_ticks = 40;velocity = 0
		"sustain":
			if height > 0: velocity = clampf(velocity+launch,-70,150)
			else: velocity = maxf(velocity,minf(launch,140))
		"rescue":
			velocity = maxf(velocity,launch) if height < 130 else minf(velocity,70)
		_:
			if juggle_hits <= juggle_limit:velocity = maxf(velocity,launch)
	if juggle_hits > juggle_limit and not knockdown: velocity = minf(velocity,0)
	if event.has("horizontal_speed"):
		horizontal_velocity = direction*float(event.horizontal_speed)
		carry_ticks = 45
		bounce_armed = bool(event.get("wall_bounce",false)) and wall_bounces < maximum_wall_bounces
	else: horizontal_velocity = clampf(horizontal_velocity+direction*float(event.get("knockback",0))*5,-1000,1000)
	if suspended:
		cross_pending = Vector2(horizontal_velocity,velocity)
		cross_has_impulse = true
		if knockdown: release_cross()
func advance() -> void:
	recoil_left=maxi(0,recoil_left-1)
	electrical_ticks=maxi(0,electrical_ticks-1)
	electrical_cooldown=maxi(0,electrical_cooldown-1)
	if owner==Owner.Cinematic:
		capture_left-=1;capture_age+=1
		# Only this owner writes cinematic movement; no ordinary gravity/wall integration.
		height=lerpf(captured_height,capture_goal_height,smoothstep(0,28,capture_age))
		displacement=captured_x
		if capture_left<=0:end_capture(capture_id)
		return
	if electrical_ticks>0:
		stun_ticks=maxi(stun_ticks,electrical_ticks)
		horizontal_velocity*=.92
	if cross_ticks > 0:
		cross_ticks -= 1
		if cross_ticks == 0: release_cross()
		return
	stun_ticks = maxi(0,stun_ticks-1)
	var previous_x := origin_x + displacement
	var next_x := previous_x + horizontal_velocity/60
	var crossed := (next_x >= wall_right and horizontal_velocity > 0) or (next_x <= wall_left and horizontal_velocity < 0)
	displacement = clampf(next_x,wall_left,wall_right)-origin_x
	if crossed:
		if bounce_armed and wall_bounces < maximum_wall_bounces and not knockdown:
			wall_bounces += 1
			horizontal_velocity = -signf(horizontal_velocity)*300
			velocity = maxf(velocity,260)
			stun_ticks = maxi(stun_ticks,45)
			wall_events.append({"x":origin_x+displacement,"height":height,"number":wall_bounces})
			carry_ticks = 15
		else: horizontal_velocity = 0
		bounce_armed = false
	carry_ticks = maxi(0,carry_ticks-1)
	if carry_ticks == 0: bounce_armed = false
	horizontal_velocity = move_toward(horizontal_velocity,0,3.0 if carry_ticks > 0 else 14.0)
	if recovery_ticks > 0:
		recovery_ticks -= 1
		if recovery_ticks == 0: knockdown = false
	if height > 0 or velocity > 0:
		velocity -= gravity/60
		height = clampf(height+velocity/60,0,maximum_height)
		if height >= maximum_height: velocity = minf(velocity,0)
		if height == 0:
			velocity = 0
			if knockdown: recovery_ticks = 40
	# Limits reset on genuine neutral recovery, not every contact with the floor.
	if settled():
		juggle_hits=0;wall_bounces=0;bounce_armed=false;launch_count=0;stun_budget=maximum_stun_budget;suspension_used=0;electrical_uses=0
func state_name() -> String:
	if owner==Owner.Cinematic:return "CINEMATIC CAPTURE"
	if electrical_ticks>0:return "ELECTRICAL %dt" % electrical_ticks
	if cross_ticks > 0:return "CROSS SUSPENSION"
	if knockdown:return "KNOCKDOWN / RECOVERY"
	if height > 0:return "RISING" if velocity > 0 else "FALLING"
	return "HITSTUN" if stun_ticks > 0 else "GROUNDED"
func settled() -> bool:
	return owner==Owner.Ordinary and electrical_ticks==0 and height == 0 and stun_ticks == 0 and recovery_ticks == 0 and cross_ticks == 0
func reset() -> void:
	owner=Owner.Ordinary;capture_id=-1;capture_left=0;capture_age=0;capture_goal_height=70;recoil_left=0;electrical_ticks=0;electrical_cooldown=0;electrical_uses=0;launch_count=0;stun_budget=maximum_stun_budget;suspension_used=0
	height=0;velocity=0;displacement=0;horizontal_velocity=0;stun_ticks=0;cross_ticks=0;juggle_hits=0;knockdown=false;recovery_ticks=0
	wall_bounces=0;bounce_armed=false;carry_ticks=0;wall_events.clear();cross_saved=Vector2.ZERO;cross_pending=Vector2.ZERO;cross_has_impulse=false;cross_releases=0
