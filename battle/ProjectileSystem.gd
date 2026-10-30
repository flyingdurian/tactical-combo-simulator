class_name ProjectileSystem
extends Node2D
## Visible arrows, swept segment contact, one hit per projectile, no homing.
signal connected(shot: Dictionary, region: Rect2)
signal missed(shot: Dictionary, region: Rect2)
var shots: Array[Dictionary] = []
var spawned: Dictionary = {}
func fire(actor: int, move: SequenceData, event: Dictionary, token: String, fighter: BattleActor, context: Dictionary) -> void:
	if spawned.has(token): return
	spawned[token] = true
	var origin: Array = event.get("origin", [88,-114])
	var at := fighter.position + Vector2(float(origin[0])*fighter.facing, float(origin[1])-fighter.elevation)
	if event.has("origin_anchor"):
		at=fighter.anchor_world(str(event.origin_anchor),Vector2(origin[0],origin[1]))
	var angle_authored:=float(event.get("aim_angle",0))
	var direction:=Vector2(fighter.facing*cos(angle_authored),sin(angle_authored))
	if event.get("aim_snapshot",false):
		var difference: Vector2 = context.aim-at
		var angle := clampf(atan2(difference.y,absf(difference.x)),-.45,.45)
		direction = Vector2(fighter.facing*cos(angle),sin(angle))
	shots.append({"actor":actor,"move":move,"event":event,"token":token,"at":at,"previous":at,"facing":fighter.facing,
		"ttl":int(event.get("flight_ticks",35)),"velocity":direction*float(event.get("speed",1500))/60,"context":context,"closest":Rect2()})
	queue_redraw()
func advance(player_target: Rect2,cpu_target:Rect2=Rect2()) -> void:
	for shot in shots.duplicate():
		var target:Rect2=cpu_target if shot.actor>=3 else player_target
		shot.previous = shot.at
		shot.at += shot.velocity
		shot.ttl -= 1
		var region := Rect2(Vector2(minf(shot.at.x,shot.previous.x)-4,minf(shot.at.y,shot.previous.y)-5),Vector2(absf(shot.at.x-shot.previous.x)+8,absf(shot.at.y-shot.previous.y)+10))
		if region.end.x >= target.position.x and region.position.x <= target.end.x: shot.closest = region
		if region.intersects(target):
			connected.emit(shot, region)
			shots.erase(shot)
		elif shot.ttl <= 0 or shot.at.x < -40 or shot.at.x > 1320:
			missed.emit(shot, shot.closest if shot.closest.has_area() else region)
			shots.erase(shot)
	queue_redraw()
func cancel_owned(action_id: int) -> void:
	shots = shots.filter(func(shot: Dictionary) -> bool: return int(shot.token.split(":")[1]) != action_id)
	queue_redraw()
func reset() -> void:
	shots.clear();spawned.clear();queue_redraw()
func _draw() -> void:
	for shot in shots:
		var color:=Color(str(shot.event.get("color","#97eeff")))
		var visual:=str(shot.event.get("visual","arrow"))
		if visual=="orb":
			draw_circle(shot.at,11,color*Color(1,1,1,.3));draw_circle(shot.at,6,color);draw_circle(shot.at,3,Color.WHITE)
			draw_arc(shot.at,12,0,TAU,16,color,2);continue
		if visual=="seal":
			var at:Vector2=shot.at
			draw_colored_polygon(PackedVector2Array([at+Vector2(-12,0),at+Vector2(0,-7),at+Vector2(12,0),at+Vector2(0,7)]),color)
			draw_line(at+Vector2(-8,0),at+Vector2(8,0),Color.WHITE,2);continue
		if visual=="bullet":
			draw_line(shot.at-shot.velocity.normalized()*18,shot.at,color,5);continue
		var tail: Vector2 = shot.at - shot.velocity.normalized()*32
		draw_line(tail,shot.at,Color("97eeff"),4)
		draw_line(shot.at,shot.at+Vector2(-shot.facing*10,-5),Color.WHITE,2)
		draw_line(shot.at,shot.at+Vector2(-shot.facing*10,5),Color.WHITE,2)
